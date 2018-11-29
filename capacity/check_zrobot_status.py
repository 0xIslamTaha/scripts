from gevent import monkey
monkey.patch_all()

from jumpscale import j
import click
from gevent.pool import Pool


@click.command()
@click.option("-f", "--farm_name", help="farm name to update its zrobot", required=True)
def main(farm_name):
    logger = j.logger.get('log.txt')
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': farm_name})[1]
    nodes = resp.json() #nodes
    logger.info("no. of nodes : {}".format(len(nodes)))

    def do(node):                                             
        addr=node["robot_address"][7:-5]                                
        node=j.clients.zos.get("main", data={"host":addr})
        logger = j.logger.get('log.txt')
        try:                                                                
            node.client.ping()
        except:        
            logger.error("can't reach %s node", node.addr)
            return
        try:
            if node.containers.get('zrobot').is_running():
                logger.info('running : zrobot for {} node'.format(node.addr))
            else:
                logger.warning('not running : zrobot for {} node'.format(node.addr))
        except Exception as e:
            logger.error("can't find zrorbot in {} node".format(node.addr))
            logger.error(e)

    execute_all_nodes(do, nodes=nodes)

def execute_all_nodes(func, nodes):
    """
    execute func on all the nodes
    """
    g = Pool(size=100)
    g.map(func, nodes)
    g.join()

if __name__ == '__main__':
    main()
