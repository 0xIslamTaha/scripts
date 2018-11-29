from gevent import monkey
monkey.patch_all()

from jumpscale import j
import click
from gevent.pool import Pool

@click.command()
@click.option("-f", "--farm_name", help="farm name to update its zrobot", required=True)
@click.option("-i", "--node_id", help="node id", required=True)
def main(farm_name, node_id):
    logger = j.logger.get('log.txt')
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': farm_name})[1]
    nodes = resp.json() #nodes
    logger.info("no. of nodes : {}".format(len(nodes)))
    
    for node in nodes:
        if node['node_id'] == node_id:
            addr=node["robot_address"][7:-5]                                
            logger.info('{} : {}'.format(node_id, addr))

if __name__ == '__main__':
    main()
