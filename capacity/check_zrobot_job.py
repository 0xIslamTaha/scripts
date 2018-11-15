from jumpscale import j
import click
from gevent.pool import Pool


@click.command()
@click.option("-f", "--farm_name", help="farm name to update its zrobot", required=True)
def main(farm_name):
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': farm_name})[1]
    nodes = resp.json() #nodes
    logger = j.logger.get('log.txt')
    
    def do(node):                                           
        addr=node["robot_address"][7:-5]                                
        node=j.clients.zos.get("main", data={"host":addr})
        try:                                                                
            node.client.ping()                         
        except:        
            logger.error("can't reach %s skipping", node.addr)
        try:
            node.containers.get('zrobot').stop()
            logger.info('stop zrobot for {} node'.format(node.addr))
        except:
            logger.error("can't find zrorbot in {} node".format(node.addr))

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
