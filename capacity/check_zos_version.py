from jumpscale import j
from subprocess import Popen, PIPE
import click


logger = j.logger.get('check_node_commit')



@click.command()
@click.option("-f", "--farm_name", help="farm name to update its zrobot", required=True)
@click.option("-c", "--commit_id", help="match with this commit id", default='')
def main(farm_name, commit_id):
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': farm_name})[1]
    nodes = resp.json() #nodes
    logger.info(" #Nodes : {}".format(len(nodes)))
    for node in nodes:    
        capacity_commit_id = node['os_version'].split(' ')[1]
        addr=node["robot_address"][7:-5]  

        # check node is up
        res = Popen("ping -c 1 {}".format(addr), shell=True, stdout=PIPE, stderr=PIPE)
        out = res.stdout.readlines()
        err = res.stderr.readlines()
        if err:
            logger.info(" {} node is down.".format(addr))
            continue
        try:                              
            node_client=j.clients.zos.get("main", data={"host":addr})
            real_node_commit_id = node_client.client.info.version()['revision']
        except:
            logger.error(" {} Can't get node client ... ".format(addr))
            continue

        if capacity_commit_id != real_node_commit_id:
            logger.error('{} != {}, node: {}:{}'.format(capacity_commit_id, real_node_commit_id, node['node_id'], addr))
        else:
            logger.info('node: {}:{} is okay'.format(node['node_id'], addr))

        if commit_id:
            if capacity_commit_id != commit_id:
                logger.error('{} != {}, node: {}:{}, issue in capacity logs'.format(capacity_commit_id, commit_id, node['node_id'], addr))
            if real_node_commit_id != commit_id:
                 logger.error('{} != {}, node: {}:{}, issue in real node logs'.format(real_node_commit_id, commit_id, node['node_id'], addr))


if __name__ == '__main__':
    main()
