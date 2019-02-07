from Jumpscale import j
import click, random

#python3 webgatewaytest.py -h 127.0.0.1 -p 2379 -u root -s root -w 46.105.121.25,188.165.233.148 -d google.com -i http://192.168.1.1:8080,http://192.168.1.2:8080
@click.command()
@click.option("-h", "--host", help="etcd host", required=True)
@click.option("-p", "--port", help="etcd port", required=True, type=int)
@click.option("-u", "--username", help="etcd username", required=True)
@click.option("-s", "--password", help="etcd password", required=True)
@click.option("-w", "--webgateway_public_ips", help="webgateway public ips", required=True, type=(str))
@click.option("-d", "--domain", help="specofic domain", required=True)
@click.option("-i", "--ips", help="list of IPs", required=True, type=(str))
def main(host, port, username, password, webgateway_public_ips, domain, ips):
    logger =j.core.tools.log
    etcd_instance = "etcd__{}".format(random.randint(1, 1000))
    logger('etcd instance : {}'.format(etcd_instance))
    
    webgateway = "webgateway__{}".format(random.randint(1, 1000))
    logger('webgateway instance : {}'.format(webgateway))
    
    service = "service__{}".format(random.randint(1, 1000))
    logger("service_instance : {}".format(service))

    etcd = j.clients.etcd.get(etcd_instance, host=host, port=port, user=username, password_=password)
    webgateway = j.clients.webgateway.get(name=webgateway, etcd_instance=etcd_instance, public_ips=webgateway_public_ips.split(','))
    service = webgateway.service_create(name=service)
    service.expose(domain, ips.split(','))

if __name__ == '__main__':
    main()
