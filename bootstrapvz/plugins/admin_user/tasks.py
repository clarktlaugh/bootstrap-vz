from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.initd import InstallInitScripts
import os


class AddSudoPackage(Task):
	description = 'Adding `sudo\' to the image packages'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		info.packages.add('sudo')


class CreateAdminUser(Task):
	description = 'Creating the admin user'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import log_check_call
		log_check_call(['chroot', info.root,
		                'useradd',
		                '--create-home', '--shell', '/bin/bash',
		                info.manifest.plugins['admin_user']['username']])


class PasswordlessSudo(Task):
	description = 'Allowing the admin user to use sudo without a password'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		sudo_admin_path = os.path.join(info.root, 'etc/sudoers.d/99_admin')
		username = info.manifest.plugins['admin_user']['username']
		with open(sudo_admin_path, 'w') as sudo_admin:
			sudo_admin.write('{username} ALL=(ALL) NOPASSWD:ALL'.format(username=username))
		import stat
		ug_read_only = (stat.S_IRUSR | stat.S_IRGRP)
		os.chmod(sudo_admin_path, ug_read_only)


class AdminUserCredentials(Task):
	description = 'Modifying ec2-get-credentials to copy the ssh public key to the admin user'
	phase = phases.system_modification
	predecessors = [InstallInitScripts]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		getcreds_path = os.path.join(info.root, 'etc/init.d/ec2-get-credentials')
		username = info.manifest.plugins['admin_user']['username']
		sed_i(getcreds_path, 'username=\'root\'', 'username=\'{username}\''.format(username=username))
