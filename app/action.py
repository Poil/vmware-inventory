#!/usr/bin/env python
# encoding:utf-8
'''Based on vc-api to get related data in the cluster, as a data source for CMDB storage'''

import os
import ssl
import requests
from pyVim import connect
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
                for datastore in datastores:
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
        return cluster_list

    def v_get_cluster(self, filter_dc=None):
        """ Get the cluster name, memory, cpu, status, and other related attributes and return the cluster as a list """
        #cluster_list = []
        cls = {}
        datacenters = self.v_get_object()
        for dc in datacenters:
            cls[dc.name] = {}
            if filter_dc is None or filter_dc == dc.name:
                clusters = dc.hostFolder.childEntity
                for cluster in clusters:
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
        return host_list

    #def v_get_vhost_physical_net(self, filter_cl=None):
    #    """ Get host's physical network information based on host """
    #    host_list = self.vi_get_vhost(filter_cl)
    #    print 'host_name device pci driver wakeOnLanSupported mac autoNegotiateSupported'
    #    for host in host_list:
    #        host_name = host.name
    #        try:
    #            for pnic in host.config.network.pnic:
    #                device = pnic.device
    #                pci = pnic.pci
    #                driver = pnic.driver
    #                wakeOnLanSupported = pnic.wakeOnLanSupported
    #                mac = pnic.mac
    #                autoNegotiateSupported = pnic.autoNegotiateSupported

    #                print host_name,device,pci,driver,wakeOnLanSupported,mac,autoNegotiateSupported
    #        except AttributeError:
    #            pass


    #def v_get_vhost_vswitch(self, filter_cl):
    #    # Get the host's vswitch based on host
    #    host_list = self.vi_get_vhost(filter_cl)
    #    print 'host_name vs_name vs_key numPorts is_bond numPortsAvailable physicalDevice'
    #    for host in host_list:
    #        try:
    #            for vs in host.config.network.vswitch:
    #                host_name = host.name
    #                vs_name = vs.name
    #                vs_key = vs.key
    #                numPorts = vs.numPorts
    #                is_bond = 0
    #                numPortsAvailable = vs.numPortsAvailable
    #                numnicDevice = len(vs.spec.bridge.nicDevice)
    #                physicalDevice = []
    #                if numnicDevice == 2:
    #                    is_bond = 1
    #                    physicalDevice.append(vs.spec.bridge.nicDevice[0])
    #                    physicalDevice.append(vs.spec.bridge.nicDevice[1])
    #                else:
    #                    physicalDevice.append(vs.spec.bridge.nicDevice[0])
    #                print host_name, vs_name, vs_key, numPorts, is_bond, numPortsAvailable, physicalDevice
    #        except AttributeError:
    #            pass

    def v_get_vhost_portgroup(self, filter_cl=None):
        """ Get portgroup based on host and associate with vswitch key """
        host_list = self.vi_get_vhost(filter_cl)
        pgs = {}
        for host in host_list:
            try:
                for ps in host.config.network.portgroup:
                    vswitch_name = ps.spec.vswitchName
                    if vswitch_name not in pgs:
                        pgs[vswitch_name] = {}

                    ps_name = ps.spec.name
                    if ps_name not in pgs[vswitch_name]:
                        pgs[vswitch_name][ps_name] = {}

                    for m in ['name', 'vlanId']:
                        pgs[vswitch_name][ps_name][m] = getattr(ps.spec, m)
                    for m in ['key']:
                        pgs[vswitch_name][ps_name][m] = getattr(ps, m)

            except AttributeError:
                pass
        return pgs

    #def v_get_vms(self, filter_cl=None):
    #    """ According to the host to get the relevant information of vm """
    #    host_list = self.vi_get_vhost(filter_cl)
    #    print 'host_name;vm_name;instance_UUID;bios_UUID;guest_os_name;connectionState;path_to_vm;guest_tools_status;memorySizeMB;numCpu;numVirtualDisks;disk_committed;disk_uncommitted;disk_unshared;powerState;overallStatus;last_booted_timestamp;ip_list;macAddress;prot_group'
    #    for host in host_list:
    #        for vm in host.vm:
    #            host_name = host.name
    #            vm_name = vm.name
    #            instance_UUID = vm.summary.config.instanceUuid
    #            bios_UUID = vm.summary.config.uuid
    #            guest_os_name = vm.summary.config.guestFullName
    #            connectionState = vm.summary.runtime.connectionState
    #            path_to_vm = vm.summary.config.vmPathName
    #            guest_tools_status = vm.guest.toolsStatus
    #            memorySizeMB = vm.summary.config.memorySizeMB
    #            numCpu = vm.summary.config.numCpu
    #            numVirtualDisks = vm.summary.config.numVirtualDisks
    #            disk_committed = vm.summary.storage.committed
    #            disk_uncommitted = vm.summary.storage.uncommitted
    #            disk_unshared = vm.summary.storage.unshared
    #            powerState = vm.summary.runtime.powerState
    #            overallStatus = vm.summary.overallStatus
    #            last_booted_timestamp = vm.runtime.bootTime
    #            ip_list = []
    #            for vnic in vm.guest.net:
    #                prot_group = vnic.network
    #                ips = vnic.ipAddress
    #                for ip in ips:
    #                    ip_list.append(ip)
    #                macAddress = vnic.macAddress

    #            print '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' %(host_name, vm_name, instance_UUID, bios_UUID, guest_os_name, connectionState, path_to_vm, guest_tools_status, memorySizeMB, numCpu, numVirtualDisks, disk_committed, disk_uncommitted, disk_unshared, powerState, overallStatus, last_booted_timestamp, ip_list, macAddress, prot_group)

    def v_get_vm_template(self):
        """ get vm template """
        vms = self.v_get_object_type(vim.VirtualMachine)
        tpls = []
        for vm in vms:
            if vm.config.template:
                tpls.append(vm.name)
        return tpls

    def v_server_disconnect(self):
        """ sign out """
        connect.Disconnect(self.v_server_connect())
        return True


#if __name__ == '__main__':
#    run = Action()
#    run.v_check_login()
#
#    print json.dumps(run.v_get_datacenter())
#    print json.dumps(run.v_get_datastore())
#    print json.dumps(run.v_get_cluster())
#    #run.v_get_vhost()
#    #run.v_get_vhost_physical_net()
#    #run.v_get_vhost_vswitch()
#    print json.dumps(run.v_get_vhost_portgroup('FRFSSL-LABCVY-CLUSTER-CUSTOMER'))
#    #run.v_get_vms()
#    run.v_server_disconnect()
#    del run
