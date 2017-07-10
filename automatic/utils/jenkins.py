import json
import socket
from http.client import *
from urllib.error import *
from urllib.parse import quote, urlencode
from urllib.request import *

LAUNCHER_SSH = 'hudson.plugins.sshslaves.SSHLauncher'
LAUNCHER_COMMAND = 'hudson.slaves.CommandLauncher'
LAUNCHER_JNLP = 'hudson.slaves.JNLPLauncher'
LAUNCHER_WINDOWS_SERVICE = 'hudson.os.windows.ManagedWindowsServiceLauncher'

INFO = 'api/json'
PLUGIN_INFO = 'pluginManager/api/json?depth=%(depth)s'
CRUMB_URL = 'crumbIssuer/api/json'
JOB_INFO = 'job/%(name)s/api/json?depth=%(depth)s'
JOB_NAME = 'job/%(name)s/api/json?tree=name'
Q_INFO = 'queue/api/json?depth=0'
Q_ITEM = 'queue/item/%(id)s/api/xml'
Q_ITEM_MARKER = 'queue/item/'
CANCEL_QUEUE = 'queue/cancelItem?id=%(id)s'
CREATE_JOB = 'createItem?name=%(name)s'  # also post config.xml
CONFIG_JOB = 'job/%(name)s/config.xml'
DELETE_JOB = 'job/%(name)s/doDelete'
ENABLE_JOB = 'job/%(name)s/enable'
DISABLE_JOB = 'job/%(name)s/disable'
COPY_JOB = 'createItem?name=%(to_name)s&mode=copy&from=%(from_name)s'
RENAME_JOB = 'job/%(from_name)s/doRename?newName=%(to_name)s'
BUILD_JOB = 'job/%(name)s/build'
STOP_BUILD = 'job/%(name)s/%(number)s/stop'
BUILD_WITH_PARAMS_JOB = 'job/%(name)s/buildWithParameters'
BUILD_INFO = 'job/%(name)s/%(number)d/api/json?depth=%(depth)s'
BUILD_CONSOLE_OUTPUT = 'job/%(name)s/%(number)d/consoleText'

CREATE_NODE = 'computer/doCreateItem?%s'
DELETE_NODE = 'computer/%(name)s/doDelete'
NODE_INFO = 'computer/%(name)s/api/json?depth=%(depth)s'
NODE_TYPE = 'hudson.slaves.DumbSlave$DescriptorImpl'
TOGGLE_OFFLINE = 'computer/%(name)s/toggleOffline?offlineMessage=%(msg)s'
CONFIG_NODE = 'computer/%(name)s/config.xml'

# for testing only
EMPTY_CONFIG_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
	<keepDependencies>false</keepDependencies>
	<properties/>
	<scm class='jenkins.scm.NullSCM'/>
	<canRoam>true</canRoam>
	<disabled>false</disabled>
	<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
	<triggers class='vector'/>
	<concurrentBuild>false</concurrentBuild>
	<builders/>
	<publishers/>
	<buildWrappers/>
</project>'''

# for testing only
RECONFIG_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
	<keepDependencies>false</keepDependencies>
	<properties/>
	<scm class='jenkins.scm.NullSCM'/>
	<canRoam>true</canRoam>
	<disabled>false</disabled>
	<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
	<triggers class='vector'/>
	<concurrentBuild>false</concurrentBuild>
	<builders>
		<jenkins.tasks.Shell>
			<command>export FOO=bar</command>
		</jenkins.tasks.Shell>
	</builders>
	<publishers/>
	<buildWrappers/>
</project>'''


class JenkinsException(Exception):
    '''General exception type for jenkins-API-related failures.'''
    pass


class NotFoundException(JenkinsException):
    '''A special exception to call out the case of receiving a 404.'''
    pass


class EmptyResponseException(JenkinsException):
    '''A special exception to call out the case receiving an empty response.'''
    pass


class BadHTTPException(JenkinsException):
    '''A special exception to call out the case of a broken HTTP response.'''
    pass


def auth_headers(username, password):
    '''Simple implementation of HTTP Basic Authentication.
    Returns the 'Authentication' header value.
    '''
    auth = '%s:%s' % (username, password)
    # if isinstance(auth, six.text_type):
    # auth = auth.encode('utf-8')
    #return b'Basic ' + base64.b64encode(auth)
    return auth


class Jenkins():
    def __init__(self, url, username=None, password=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if url[-1] == '/':
            self.server = url
        else:
            self.server = url + '/'
        if username is not None and password is not None:
            self.auth = auth_headers(username, password)
        else:
            self.auth = None
        self.timeout = timeout

    def _get_encoded_params(self, params):
        for k, v in params.items():
            if k in ["name", "to_name", "from_name", "msg"]:
                params[k] = quote(v)
        return params

    def jenkins_open(self, req):
        try:
            if self.auth:
                req.add_header('Authorization', self.auth)
            response = urlopen(req, timeout=self.timeout)
            response_text = response.read().decode('utf-8')
            if response_text is None:
                raise EmptyResponseException("Error communicating with server[%s]: empty response" % self.server)
            return (response_text, response)
        except HTTPError as e:
            if e.code in [401, 403, 500]:
                raise JenkinsException(
                    'Error in request. ' + 'Possibly authentication failed [%s]: %s' % (e.code, e.msg))
            elif e.code == 404:
                raise NotFoundException('Requested item could not be found')
            else:
                raise
        except URLError as e:
            raise JenkinsException('Error in request: %s' % (e.reason))

    def get_info(self):
        try:
            response_text, response = self.jenkins_open(Request(self.server + INFO))
            return json.loads(response_text)
        except (HTTPError, BadStatusLine):
            raise BadHTTPException("Error communicating with server[%s]" % self.server)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for server[%s]" % self.server)

    def build_job_url(self, name, parameters=None, token=None):
        if parameters:
            if token:
                parameters['token'] = token
            r_v = self.server + BUILD_WITH_PARAMS_JOB % self._get_encoded_params(locals()) + '?' + urlencode(parameters)
        elif token:
            r_v = self.server + BUILD_JOB % self._get_encoded_params(locals()) + '?' + urlencode({'token': token})
        else:
            r_v = self.server + BUILD_JOB % self._get_encoded_params(locals())
        return r_v

    def build_job(self, name, parameters=None, token=None):
        '''Trigger build job.
        :param name: name of job
        :param parameters: parameters for job, or ``None``, ``dict``
        :param token: Jenkins API token
        '''
        response_text, response = self.jenkins_open(
            Request(self.build_job_url(name, parameters, token), "".encode('utf-8')))
        queue_id = '-1'
        if response.status == 201:
            queue_str = response.getheader('Location')
            if queue_str[-1] == '/':
                queue_str = queue_str[:-1]
            marker_index = queue_str.rfind(Q_ITEM_MARKER)
            if marker_index > -1:
                queue_id = queue_str[marker_index + len(Q_ITEM_MARKER):]
        return queue_id

    def get_q_item_url(self, q_id):
        return self.server + Q_ITEM % {'id': q_id}
