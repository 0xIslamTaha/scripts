from jumpscale import j
import click

@click.command()
@click.option("-f", "--farm_name", help="farm name to update its zrobot", required=True)
def main(farm_name):
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': farm_name})[1]
    nodes = resp.json() #nodes
    for node in nodes:                                             
        addr=node["robot_address"][7:-5]                                
        node=j.clients.zos.get("main", data={"host":addr})
        logger = j.logger.get('log.txt')
        try:                                                                
            node.client.ping()                         
        except:        
            logger.error(" can't reach %s skipping", node.addr)
            continue   
        try:
            node.containers.get('zrobot').stop()
            logger.info(' stop zrobot for {} node'.format(node.addr))
        except:
            logger.error(" can't find zrorbot in {} node".format(node.addr))

if __name__ == '__main__':
    main()
