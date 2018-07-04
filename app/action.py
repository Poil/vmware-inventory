#!/usr/bin/env python
# encoding:utf-8
'''Based on vc-api to get related data in the cluster, as a data source for CMDB storage'''

import ssl
import requests
from pyVim import connect
from pyVim.task import WaitForTask
from pyVmomi import vim


class Action(object):
    """ Action """

    def __init__(self, v_server, v_user, v_passwd):
        self.v_server = v_server
        self.v_user = v_user
        self.v_passwd = v_passwd

    def v_server_connect(self):
        """ Link vcenter-api to try to login """
        requests.packages.urllib3.disable_warnings()
        if hasattr(ssl, '_create_unverified_context'):
           ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None

        try:
            service_instance = connect.SmartConnect(
                host=self.v_server,
                user=self.v_user,
                pwd=self.v_passwd,
                port=443,
                sslContext=ssl_context,
                connectionPoolTimeout=0)
            return service_instance
        except:
            return False

    def v_check_login(self):
        """ Get logged in session id """
        session_id = self.v_server_connect().content.sessionManager.currentSession.key
        return session_id

    def v_get_object(self):
        """ Use the rootFolder method """
        vc_rootFolder = self.v_server_connect().RetrieveContent().rootFolder
        datacenters = vc_rootFolder.childEntity
        return datacenters

    def v_get_object_type(self, vim_type):
        """ get object type """
        content = self.v_server_connect().RetrieveContent()
        return [item for item in content.viewManager.CreateContainerView(
            content.rootFolder, [vim_type], recursive=True).view]

    def v_get_datacenter(self):
        """ Get storage cluster """
        datacenters = self.v_get_object()
        return [dc.name for dc in datacenters]

    def v_get_datastore(self, filter_dc=None):
        """ Get a single store """
        datacenters = self.v_get_object()
        ds = {}
        for dc in datacenters:
            dc_name = dc.name
            if filter_dc is None or filter_dc == dc_name:
                ds[dc_name] = {}
                datastores = dc.datastoreFolder.childEntity
                for datastore in sorted(datastores):
                    summary = datastore.summary
                    ds[dc_name][summary.name] = {}
                    for m in ['capacity', 'freeSpace']:
                        ds[dc_name][summary.name][m] = getattr(summary, m)
        return ds

    def vi_get_cluster(self):
        """ Get the cluster name, memory, cpu, status, and other related attributes and return the cluster as a list """
        cluster_list = []
        datacenters = self.v_get_object()
        for dc in datacenters:
            clusters = dc.hostFolder.childEntity
            for cluster in clusters:
                cluster_list.append(cluster)
        return sorted(cluster_list)

    def v_get_cluster(self, filter_dc=None):
        """ Get the cluster name, memory, cpu, status, and other related attributes and return the cluster as a list """
        #cluster_list = []
        cls = {}
        datacenters = self.v_get_object()
        for dc in datacenters:
            cls[dc.name] = {}
            if filter_dc is None or filter_dc == dc.name:
                clusters = dc.hostFolder.childEntity
                for cluster in sorted(clusters):
                    name = cluster.name
                    cls[dc.name][name] = {}
                    summary = cluster.summary
                    for m in ['totalCpu', 'totalMemory', 'numCpuCores', 'numCpuThreads', 'effectiveCpu',
                              'effectiveMemory', 'overallStatus']:
                        cls[dc.name][name][m] = getattr(summary, m)
        return cls

    def vi_get_vhost(self, filter_cl=None):
        """ Get the list of clusters and get the host through cluster """
        host_list = []
        clusters = self.vi_get_cluster()
        for cluster in clusters:
            if filter_cl is None or filter_cl == cluster.name:
                hosts = cluster.host
                for host in hosts:
                    host_list.append(host)
        return sorted(host_list)

    def v_get_vdswitch(self, filter_dc=None):
        """ vdswitch """
        datacenters = self.v_get_object()
        vds = {}
        for dc in datacenters:
            dc_name = dc.name
            if filter_dc is None or filter_dc == dc_name:
                vds[dc_name] = []
                vdswitches = dc.networkFolder.childEntity
                for vdswitch in sorted(vdswitches):
                    if isinstance(vdswitch, vim.DistributedVirtualSwitch):
                        summary = vdswitch.summary
                        vds[dc_name].append(summary.name)
        return vds

    def vi_get_vdswitch(self, filter_dc, filter_vdswitch):
        """ internal function vdswitch """
        datacenters = self.v_get_object()
        for dc in datacenters:
            dc_name = dc.name
            if filter_dc == dc_name:
                vdswitches = dc.networkFolder.childEntity
                for vdswitch in vdswitches:
                    if isinstance(vdswitch, vim.DistributedVirtualSwitch):
                        if filter_vdswitch == vdswitch.summary.name:
                            return vdswitch
        return None


    def v_get_vdportgroup(self, filter_dc, vdswitch_name):
        """ vdportgroup """
        vdswitch = self.vi_get_vdswitch(filter_dc, vdswitch_name)
        return sorted([vdportgroup.name for vdportgroup in vdswitch.portgroup])

    def v_get_folder(self, filter_dc=None, filter_ds=None):
        """ folder """
        fds = {}
        spec = vim.host.DatastoreBrowser.SearchSpec(query=[vim.host.DatastoreBrowser.FolderQuery()])
        for dc in self.v_server_connect().content.rootFolder.childEntity:
            fds[dc.name] = {}
            if filter_dc is None or filter_dc == dc.name:
                for ds in dc.datastore:
                    fds[dc.name][ds.name] = []
                    if filter_ds is None or filter_ds == ds.name:
                        task = ds.browser.SearchSubFolders("[%s]" % ds.name, spec)
                        WaitForTask(task)
                        for result in task.info.result:
                            for fileInfo in sorted(result.file):
                                fds[dc.name][ds.name].append(result.folderPath+'/'+fileInfo.path)
        return fds

    def v_get_vmfolder(self, filter_dc=None):
        """ vm folder """
        datacenters = self.v_server_connect().content.rootFolder.childEntity
        vmfds = {}
        for dc in datacenters:
            vmFolders = dc.vmFolder.childEntity
            if filter_dc is None or filter_dc == dc.name:
                return sorted([folder.name for folder in vmFolders])
            else:
                for folder in sorted(vmFolders):
                    vmfds[dc.name] = []
                    vmfds[dc.name].append(folder.name)


    def v_get_vm_template(self):
        """ get vm template """
        vms = self.v_get_object_type(vim.VirtualMachine)
        tpls = []
        for vm in vms:
            if vm.config.template:
                tpls.append(vm.name)
        return sorted(tpls)

    def v_server_disconnect(self):
        """ sign out """
        connect.Disconnect(self.v_server_connect())
        return True
