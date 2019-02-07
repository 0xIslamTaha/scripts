from Jumpscale import j
import click, random

#python3 webgatewaytest.py -h 127.0.0.1 -p 2379 -u root -s root -d google.com -i http://192.168.1.1:8080,http://192.168.1.2:8080
@click.command()
@click.option("-h", "--host", help="etcd host", required=True)
@click.option("-p", "--port", help="etcd port", required=True, type=int)
@click.option("-u", "--username", help="etcd username", required=True)
@click.option("-s", "--password", help="etcd password", required=True)
@click.option("-d", "--domain", help="specofic domain", required=True)
@click.option("-i", "--ips", help="list of IPs", required=True, type=(str))
def main(host, port, username, password, domain, ips):
    logger =j.core.tools.log
    etcd_instance = "etcd__{}".format(random.randint(1, 1000))
    logger('etcd instance : {}'.format(etcd_instance))
    
    webgateway = "webgateway__{}".format(random.randint(1, 1000))
    logger('webgateway instance : {}'.format(webgateway))
    
    service = "service__{}".format(random.randint(1, 1000))
    logger("service_instance : {}".format(service))

    etcd = j.clients.etcd.get(etcd_instance, host=host, port=port, user=username, password_=password)
    webgateway = j.clients.webgateway.get(name=webgateway, etcd_instance=etcd_instance)
    service = webgateway.service_create(name=service)
    service.expose(domain, ips.split(','))

if __name__ == '__main__':
    main()
