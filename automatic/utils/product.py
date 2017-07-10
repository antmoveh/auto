import datetime
from automatic.models import *


def get_products(p_id):
    prods = Product.objects.filter(active='Y')
    p_list = []
    for p in prods:
        selected = 0
        if p_id is not None and p_id == p.id:
            selected = 1
        p_list.append([p.id, p.name, selected])
    return p_list


def get_deploy_builds(p_id, bid=None, v_id=None, verified=False, no_failed=True):
    try:
        prod = Product.objects.get(id=p_id)
        branchs = prod.branchs.all().order_by('-id')
        branch_list = []
        build_list = {}
        for branch in branchs:
            selected = 0
            if bid is not None and bid == branch.id:
                selected = 1
            branch_list.append([branch.id, branch.branch, selected])
            vers = branch.versions.filter(status='D').order_by('-id')
            if verified:
                vers = vers.filter(certified='Y')
            ver_list = []
            for ver in vers:
                selected = 0
                if v_id is not None and v_id == ver.id:
                    selected = 1
                ver_list.append([ver.id, str(ver.v_bn), selected])
            build_list[str(branch.id)] = ver_list
    except Exception as e:
        return {'branch_list': [], 'build_list': {}}
    return {'branch_list': branch_list, 'build_list': build_list}


def get_builds(p_id, b_id, start=None, step=None):
    if start is None:
        start = 0
    if step is None:
        step = 20
    try:
        prod = Product.objects.get(id=p_id)
        branch = prod.branchs.get(id=b_id)
        vers = branch.versions.all().order_by('-id')
        count = len(vers)
        vers = vers[start: start + step]
        build_list = []
        tz_diff = datetime.timedelta(hours=8)
        for ver in vers:
            build_list.append(
                [ver.id, ver.version, ver.build_master.display, str(ver.build_time + tz_diff), ver.status])
    except Exception as e:
        return {'total': 0, 'builds': []}
    return {'total': count, 'builds': build_list}


def get_product(pid):
    try:
        prod = Product.objects.get(id=pid)
    except Exception as e:
        return None
    else:
        return prod.name


def get_branchs(pid, bid=None):
    prod = Product.objects.get(id=pid)
    branchs = prod.branchs.all().order_by('-id')
    if bid is not None:
        try:
            bid = int(bid)
        except ValueError as e:
            bid = None
    current_branch = None
    branch_list = []
    for branch in branchs:
        selected = 0
        if bid is None:
            bid = branch.id
            current_branch = branch.id
            selected = 1
        else:
            if bid == branch.id:
                current_branch = branch.id
                selected = 1
        branch_list.append([branch.id, branch.branch, selected])
    return (current_branch, branch_list)


def get_version(vid):
    tz_diff = datetime.timedelta(hours=8)
    try:
        ver = Prod_Version.objects.get(id=int(vid))
        builds = ver.builds.all()
        build_list = []
        for build in builds:
            bj = build.bj
            url = ""
            if len(build.b_id) > 0:
                jenkins = bj.jenkins.url
                if jenkins[-1] != '/':
                    jenkins += '/'
                url = jenkins + 'job/' + bj.job_name + '/' + build.b_id + '/console'
            build_list.append({'module': bj.module.name, 'rev': build.rev, 'status': build.status, 'url': url})
        v = {
            'id': ver.id,
            'prod_id': ver.prod.id,
            'version': ver.version,
            'v_bn': ver.v_bn,
            'builds': build_list,
            'build_master': ver.build_master,
            'build_time': str(ver.build_time + tz_diff),
            'descript': ver.descript,
            'status': ver.status,
            'certified': ver.certified,
        }
    except:
        return None
    return v


def get_branch(bid):
    try:
        branch = Prod_Branch.objects.get(id=int(bid))
        b = {
            'id': branch.id,
            'prod_id': branch.prod_id,
            'branch': branch.branch,
        }
    except Exception as e:
        return None
    else:
        return b


def get_servers(vid):
    tz_diff = datetime.timedelta(hours=8)
    servers = []
    try:
        ver = Prod_Version.objects.get(id=vid)
        dep_details = Dep_Status.objects.filter(version=ver)
        all_server = Dep_Server.objects.filter(active='Y')
        for s in all_server:
            detail = dep_details.filter(server=s).order_by('-id')
            if len(detail) > 0:
                dep = detail[0]
                server = {
                    'server': dep.server.server,
                    'time': str(dep.dep_time + tz_diff),
                    'username': dep.dep_user.display,
                    'desc': dep.description,
                    'status': dep.dep_status,
                    'on': dep.on_server,
                }
                servers.append(server)
    except Exception as e:
        return servers
    return servers
