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
            logger.error("can't reach %s node", node.addr)
            continue
        try:
            if node.containers.get('zrobot').is_running():
                logger.info('running : zrobot for {} node'.format(node.addr))
            else:
                logger.warning('not running : zrobot for {} node'.format(node.addr))
        except Exception as e:
            logger.error("can't find zrorbot in {} node".format(node.addr))

if __name__ == '__main__':
    main()
