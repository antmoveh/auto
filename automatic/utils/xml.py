import xml.etree.ElementTree as ET


class JENKINS_XML():
    SCM_CLASS_GIT = 'hudson.plugins.git.GitSCM'
    SCM_PLUGIN_GIT = 'git@2.3.5'
    CREDENTIALID = 'a4940cdf-ac2f-4235-a6c9-5bce0817a9a1'
    DEFAULT_XML = '''
<project>
  <actions/>
  <description></description>
  <logRotator class="hudson.tasks.LogRotator">
    <daysToKeep>30</daysToKeep>
    <numToKeep>50</numToKeep>
    <artifactDaysToKeep>7</artifactDaysToKeep>
    <artifactNumToKeep>10</artifactNumToKeep>
  </logRotator>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>id</name>
          <description></description>
          <defaultValue>-1</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>prod</name>
          <description></description>
          <defaultValue>prod</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>branch</name>
          <description></description>
          <defaultValue>-1</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>buildnumber</name>
          <description></description>
          <defaultValue>-1</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>module</name>
          <description></description>
          <defaultValue>module</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>bsp</name>
          <description></description>
          <defaultValue>&apos;&apos;</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
    <com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@1.22">
      <autoRebuild>false</autoRebuild>
    </com.sonyericsson.rebuild.RebuildSettings>
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@2.3.5">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>https://coding.net/komovie/movie-service.git</url>
        <credentialsId>a4940cdf-ac2f-4235-a6c9-5bce0817a9a1</credentialsId>
      </hudson.plugins.git.UserRemoteConfig>
      <hudson.plugins.git.UserRemoteConfig>
        <url>https://coding.net/komovie/movie-service2.git</url>
        <credentialsId>a4940cdf-ac2f-4235-a6c9-5bce0817a9a1</credentialsId>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/master</name>
      </hudson.plugins.git.BranchSpec>
      <hudson.plugins.git.BranchSpec>
        <name>test branch</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <submoduleCfg class="list"/>
    <extensions/>
  </scm>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <authToken>KoK0ZuIZ3</authToken>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>wget &quot;http://${bsp}/build/?a=start&amp;bid=${id}&amp;rev=${GIT_COMMIT}&quot; -O &quot;${WORKSPACE}/start&quot;;
bf=&quot;${build_folder}${prod}/${prod}-${branch}/${prod}-${buildnumber}/${module}/&quot;;
if [ ! -d &quot;${bf}&quot; ]; then
    mkdir -p &quot;${bf}&quot;;
fi
sed -i &quot;s/org-springside/org.springside/g&quot; &quot;${WORKSPACE}/pom.xml&quot;
#sed -i -e &quot;1,/RE/s/&lt;\!--//g&quot; &quot;${WORKSPACE}/pom.xml&quot;
#sed -i -e &quot;1,/RE/s/--&gt;//g&quot; &quot;${WORKSPACE}/pom.xml&quot;</command>
    </hudson.tasks.Shell>
    <hudson.tasks.Maven>
      <targets>clean install</targets>
      <mavenName>maven 3.2.2</mavenName>
      <properties>maven.test.skip=true</properties>
      <usePrivateRepository>false</usePrivateRepository>
      <settings class="jenkins.mvn.DefaultSettingsProvider"/>
      <globalSettings class="jenkins.mvn.DefaultGlobalSettingsProvider"/>
    </hudson.tasks.Maven>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
bf=&quot;${build_folder}${prod}/${prod}-${branch}/${prod}-${buildnumber}/${module}/&quot;;
mv &quot;${WORKSPACE}/movie-web/target/movie-couponcard.war&quot; &quot;${bf}&quot;;
wget &quot;http://${bsp}/build/?a=end&amp;bid=${id}&quot; -O &quot;${WORKSPACE}/end&quot;;</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.plugins.parameterizedtrigger.BuildTrigger plugin="parameterized-trigger@2.26">
      <configs>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.CurrentBuildParameters/>
            <hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
              <properties>status=end</properties>
            </hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
          </configs>
          <projects>BuildResult</projects>
          <condition>SUCCESS</condition>
          <triggerWithNoParameters>false</triggerWithNoParameters>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.CurrentBuildParameters/>
            <hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
              <properties>status=failed</properties>
            </hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
          </configs>
          <projects>BuildResult</projects>
          <condition>FAILED</condition>
          <triggerWithNoParameters>false</triggerWithNoParameters>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
      </configs>
    </hudson.plugins.parameterizedtrigger.BuildTrigger>
  </publishers>
  <buildWrappers>
    <org.jenkinsci.plugins.preSCMbuildstep.PreSCMBuildStepsWrapper plugin="preSCMbuildstep@0.3">
      <buildSteps>
        <hudson.tasks.Shell>
          <command>wget &quot;http://${bsp}/build/?a=cko&amp;bid=${id}&amp;jid=${BUILD_NUMBER}&quot; -O &quot;${WORKSPACE}/checkout&quot;</command>
        </hudson.tasks.Shell>
      </buildSteps>
      <failOnError>false</failOnError>
    </org.jenkinsci.plugins.preSCMbuildstep.PreSCMBuildStepsWrapper>
  </buildWrappers>
</project>
'''

    def __init__(self, filename=None):
        self.filename = filename

    def parseFile(self, f=None):
        if f is None:
            f = self.filename
        if f is None or len(f) < 1:
            return False
        try:
            self.tree = ET.parse(f)
            self.root = self.tree.getroot()
        except Exception as e:
            print(e.args[0])
            return False
        else:
            return True

    def generate_default(self):
        root = ET.fromstring(JENKINS_XML.DEFAULT_XML)

        ET.dump(root)

    def actions(self, actions=None):
        pass

    def description(self, description):
        desc = self.root.find('description')
        pass

    def get_nodes(self, tag, parent=None):
        if parent is None:
            parent = self.root
        return parent.findall(tag)

    def scm_setup(self, url, mod='git', credentialsId=None, branch='*/master', index=0):
        if url is None:
            return False
        if credentialsId is None:
            credentialsId = JENKINS_XML.CREDENTIALID
        if mod == 'git':
            scm_class = self.SCM_CLASS_GIT
            scm_plugin = self.SCM_PLUGIN_GIT
        scm = self.get_nodes(tag='scm')
        if len(scm) > 0:
            scm = scm[0]
