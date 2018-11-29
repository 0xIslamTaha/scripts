from gevent import monkey
monkey.patch_all()

from IPython import embed
from jumpscale import j
from subprocess import Popen, PIPE
from gevent.pool import Group


class capacity:
    def __init__(self, farm_name):
        self.farm_name = farm_name
        self.capacity = j.clients.threefold_directory.get(interactive=False)
        self.resp = self.capacity.api.ListCapacity(query_params={'farmer': self.farm_name})[1]
        self.nodes = self.resp.json()  # nodes
        self.logger = j.logger.get('check_node_commit')
        self.logger.info(" #Nodes : {}".format(len(self.nodes)))
        
    def check_zos_version(self, commit_id):
        def do(node):
            capacity_commit_id = node['os_version'].split(' ')[1]
            addr = node["robot_address"][7:-5]

            # check node is up
            res = Popen("ping -c 1 {}".format(addr), shell=True, stdout=PIPE, stderr=PIPE)
            err = res.stderr.readlines()
            if err:
                self.logger.info(" {} node is down.".format(addr))
            try:
                node_client = j.clients.zos.get("main", data={"host": addr})
                real_node_commit_id = node_client.client.info.version()['revision']
            except:
                self.logger.error("{} Can't get node client ... ".format(addr))
                return

            if capacity_commit_id != real_node_commit_id:
                self.logger.error(
                    '{} != {}, node: {}:{}'.format(capacity_commit_id, real_node_commit_id, node['node_id'], addr))
            else:
                self.logger.info('node: {}:{} is okay'.format(node['node_id'], addr))

            if commit_id:
                if capacity_commit_id != commit_id:
                    self.logger.error('{} != {}, node: {}:{}, issue in capacity logs'.format(capacity_commit_id, commit_id,
                                                                                        node['node_id'], addr))
                if real_node_commit_id != commit_id:
                    self.logger.error('{} != {}, node: {}:{}, issue in real node logs'.format(real_node_commit_id, commit_id,
                                                                                         node['node_id'], addr))
        self.execute_all_nodes(do, nodes=self.nodes)

    def check_zrobot_status(self):
        def do(node):
            addr = node["robot_address"][7:-5]
            node = j.clients.zos.get("main", data={"host": addr})
            try:
                node.client.ping()
            except:
                self.logger.error("can't reach %s node", node.addr)
                return
            try:
                if node.containers.get('zrobot').is_running():
                    self.logger.info('running : zrobot for {} node'.format(node.addr))
                else:
                    self.logger.warning('not running : zrobot for {} node'.format(node.addr))
                    return
            except Exception as e:
                self.logger.error("can't find zrorbot in {} node".format(node.addr))
                self.logger.error(e)

        self.execute_all_nodes(do, nodes=self.nodes)

    def get_node_ip_from_id(self, node_id):
        for node in self.nodes:
            if node['node_id'] == node_id:
                addr = node["robot_address"][7:-5]
                self.logger.info('{} : {}'.format(node_id, addr))
                return addr

    def reboot_node(self):
        def do(node):
            addr = node["robot_address"][7:-5]
            node = j.clients.zos.get("main", data={"host": addr})
            try:
                node.client.ping()
            except:
                self.logger.error("can't reach %s skipping", node.addr)
                return
            try:
                node.reboot()
                self.logger.info('reboot {} node'.format(node.addr))
            except Exception as e:
                self.logger.error("can't reboot {} node".format(node.addr))
                self.logger.error(e)

        self.execute_all_nodes(do, nodes=self.nodes)
        
    def updata_zrobot(self):
        def do(node):
            addr = node["robot_address"][7:-5]
            node = j.clients.zos.get("main", data={"host": addr})
            try:
                node.client.ping()
            except:
                self.logger.error("can't reach %s skipping", node.addr)
                return
            try:
                node.containers.get('zrobot').stop()
                self.logger.info('stop zrobot for {} node'.format(node.addr))
            except Exception as e:
                self.logger.error("can't reboot {} node".format(node.addr))
                self.logger.error(e)

        self.execute_all_nodes(do, nodes=self.nodes)

    def execute_all_nodes(self, func, nodes):
        """
        execute func on all the nodes
        """
        g = Group()
        g.map(func, nodes)
        g.join()

if __name__ == '__main__':
    embed()

