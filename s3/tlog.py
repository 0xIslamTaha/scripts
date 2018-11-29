s3 = demo.s3['s3_demo_5']
tlog = s3.service.data['data']['tlog']
robot = j.clients.zrobot.robots[tlog['node']]
robot._try_god_token()

ns = robot.services.get(name=tlog['name'])
print(ns.name)

zdb = robot.services.get(name=ns.data['data']['zerodb'])
print(zdb.name)

zdb.schedule_action('stop').wait(die=True)
zdb.schedule_action('start').wait(die=True)

new_zdb = robot.services.get(name=ns.data['data']['zerodb'])
print(new_zdb.name)
