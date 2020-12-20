#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#--------------------| INFO |-----------------------------------------#
# Este script foi criado para baixar e instalar o Navegador Tor em
# sistemas Linux e Windows.
#
#--------------------| REQUISITOS |------------------------------------#
# python 3.7 ou +
# wget para python3 - $ pip3 install wget 
#                   - > pip install wget
#
#
#--------------------| REFERÊNCIAS |-----------------------------------#
# https://www.it-swarm.dev/pt/python/argparse-module-como-adicionar-opcao-sem-nenhum-argumento/971423742/
# https://docs.python.org/dev/library/argparse.html#action
# https://stackoverflow.com/questions/3223604/how-to-create-a-temporary-directory-and-get-the-path-file-name-in-python
# https://docs.python.org/3.4/library/glob.html
#


__version__ = '2020-06-06'


import sys
import os
import re
import tempfile
import tarfile
import shutil
import argparse
import urllib.request
from subprocess import getstatusoutput
from platform import system as sys_kernel
from pathlib import Path
	
if sys_kernel() == 'Linux':
	CRed='\033[0;31m'
	CGreen='\033[0;32m'
	CYellow='\033[0;33m'
	CWhite='\033[0;37m'
	CReset='\033[m'
else:
	CRed=''
	CGreen=''
	CYellow=''
	CWhite=''
	CReset=''


# Linux ou Windows?
if (sys_kernel() != 'Linux') and (sys_kernel() != 'Windows'):
	print(f'{CRed}Execute este programa em sistemas Linux ou Windows{CReset}')
	sys.exit('1')

# root
if sys_kernel() != 'Windows':
	if os.geteuid() == int('0'):
		print(f'{CRed}Usuário não pode ser o root.{CReset}')
		sys.exit('1')

try:
	COLUMNS = int(os.get_terminal_size()[0])
except:
	COLUMNS = int(50)

class PrintText:

	def red(self, text):
		print(f'{CRed}! {text}{CReset}')

	def yellow(self, text):
		print(f'{CYellow}+ {text}{CReset}')

	def white(self, text):
		print(f'{CWhite}+  {text}{CReset}')

	def print_line(self):
		print('-' * COLUMNS)


dir_root = os.path.dirname(os.path.realpath(__file__)) # Endereço deste script no disco.
dir_run = os.getcwd()                               # Diretório onde o terminal está aberto.

# Inserir o diretório do script no PATH do python - print(sys.path)                          
# sys.os.path.insert(0, dir_root) 

tmpFile = tempfile.NamedTemporaryFile(delete=False).name
tmpDir = tempfile.TemporaryDirectory().name
os.makedirs(tmpDir)

# Criação é declaração de arquivos e diretórios.
DirHomeUser = Path.home()                                 
DirUnpackTor = os.path.abspath(os.path.join(tmpDir, 'unpack'))   
DirUserBin = os.path.abspath(os.path.join(DirHomeUser, '.local', 'bin'))
DirApplications = os.path.abspath(os.path.join(DirHomeUser, '.local', 'share', 'applications'))

DESKTOP_FILE = os.path.abspath(os.path.join(DirApplications, 'start-tor-browser.desktop'))
EXECUTABLE_TOR = os.path.abspath(os.path.join(DirUserBin, 'torbrowser'))            
DESTINATION_TOR = os.path.abspath(os.path.join(DirUserBin, 'torbrowser-amd64'))             

tor_user_dirs = {
	'DirHomeUser' : DirHomeUser,
	'tmpDir' : tmpDir,
	'DirUnpackTor' : DirUnpackTor,
	'DirUserBin' : DirUserBin,
	'DirApplications' : DirApplications
}

for X in tor_user_dirs:
	dirx = tor_user_dirs[X]
	if os.path.isdir(dirx) == False:
		print(f'Criando o diretório ... {dirx}')
		os.makedirs(dirx)
	
#-------------------------------------------------------------#
# URL = domain/version/name
#-------------------------------------------------------------#
tor_download_page='https://www.torproject.org/download'
tor_domain_server='https://dist.torproject.org/torbrowser'

user_agents = [
	'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
]

user_agent = user_agents[0]


def get_html_page(url: str) -> list:
	"""
	Recebe um url e retorna o contéudo html da página.
	"""
	RegExp = re.compile(r'^http:|^ftp:|^https|^www')
	if RegExp.findall(url) == []:
		print(f'Erro: url inválida.')
		return False

	print(f'Conectando: {url}')
	num = int(1)

	while True:
		try: 
			# html = urllib.request.urlopen(url).read()
			req = urllib.request.Request(
	    		url, 
	    		data=None, 
	    		headers={
					'User-Agent': user_agent 
					}	
				)
			html = urllib.request.urlopen(req)
		except Exception as err:
			print(err)
			if num < 4:
				print(f'Tentando novamente [{num}]')
			else:
				print('Saindo')
				break
		else:
			return (html.read().decode('utf-8'))
			break

		num += 1
		sleep(0.5)

class SetDataTor(PrintText):
	
	def __init__(self):
		self.html_page_tor = get_html_page(tor_download_page).split('\n')
		self.list_html_filter = []
		self.online_version = ''
		self.url_package = ''
		self.file_name = ''

	def get_html_filter(self, filter) -> list:
		'''
		Recebe uma string para filtar o contéudo presente em self.html_page_tor, em seguida
		retorna as ocorrências encontradas em forma de lista.
		'''
		for line in self.html_page_tor:
			if filter in line:
				self.list_html_filter.append(line)

	def set_info_tarfile(self) -> str:
		self.get_html_filter('.tar') # Filtar por ocorrências '.tar' e guardar na lista self.list_html_filter.
		RegExp = re.compile(r'torbrowser.*en-US.tar.xz\"')
		
		for line in self.list_html_filter:
			if (RegExp.search(line) != []):
				position_left = int(line.find('href="') + 6)
				position_right = int(line.rfind('"'))
				line = line[position_left : position_right] 
				break

		self.url_package = line
		self.online_version = line.split('/')[3]
		self.file_name = line.split('/')[4]

		print("Versão online ", self.online_version)
		print('Url', self.url_package)
		print('Arquivo', self.file_name)

	def set_info_winfile(self) -> str:
		self.get_html_filter('.exe') # Filtar por ocorrências '.exe' e guardar na lista self.list_html_filter.
		RegExp = re.compile(r'torbrowser.*en-US.exe\"')
		
		for line in self.list_html_filter:
			if (RegExp.search(line) != []):
				position_left = int(line.find('href="') + 6)
				position_right = int(line.rfind('"'))
				line = line[position_left : position_right] 
				break

		self.url_package = line
		self.online_version = line.split('/')[3]
		self.file_name = line.split('/')[4]

		print("Versão online ", self.online_version)
		print('Url', self.url_package)
		print('Arquivo', self.file_name)

	def set_info_osx(self) -> str:
		self.get_html_filter('.dmg') # Filtar por ocorrências '.exe' e guardar na lista self.list_html_filter.
		RegExp = re.compile(r'torbrowser.*en-US.dmg\"')
		
		for line in self.list_html_filter:
			if (RegExp.search(line) != []):
				position_left = int(line.find('href="') + 6)
				position_right = int(line.rfind('"'))
				line = line[position_left : position_right] 
				break

		self.url_package = line
		self.online_version = line.split('/')[3]
		self.file_name = line.split('/')[4]

		print("Versão online ", self.online_version)
		print('Url', self.url_package)
		print('Arquivo', self.file_name)
	

	def set_cache_dir(self):
		'''
		O arquivo será baixado no diretório de cache 
		'''
		if sys_kernel() == 'Linux':
			dirCache = (f'{DirHomeUser}/.cache/download')
		elif sys_kernel() == 'Windows':
			dirCache = ('{}\\download'.format(tmpDir))

		if os.path.isdir(dirCache) == False:
			os.makedirs(dirCache)

		return dirCache

	def set_filename_linux(self):
		self.set_info_tarfile()
		return self.file_name

	def set_torversion(self):
		for i in self.get_html_filter(): 
			if '.tar.xz' in i[-8:]:
				torVersion = i.split('/')[3]
				break

		return torVersion

	def set_linux_url(self):
		torLinux_Url = (f'{tor_domain_server}/{self.set_torversion()}/{self.set_filename_linux()}')
		return torLinux_Url

	def set_filename_windows(self):
		for i in self.get_html_filter(): 
			if '.exe' in i[-5:]:
				torFilename_Windows = os.path.basename(i)
				break

		return torFilename_Windows

	def set_windows_url(self):
		torLinux_Url = (f'{tor_domain_server}/{self.set_torversion()}/{self.set_filename_windows()}')
		return torLinux_Url


name = SetDataTor().set_filename_linux()
print(name)

exit()
print('\n')
SetDataTor().set_info_winfile()
print()
SetDataTor().set_info_osx()
exit()

class ConfigTor:
	'''
	Setar o URL de acordo com o sistema e setar o caminho completo
	de onde o arquivo deve ser baixado diretório+nome_do_arquivo.exe/.tar.xz
	'''
	if sys_kernel() == 'Linux':
		url = SetDataTor().set_linux_url()
		file = SetDataTor().set_filename_linux()  # Nome do arquivo.
		dirCache = SetDataTor().set_cache_dir()   # Pasta de download
		file = (f'{dirCache}/{file}')             # Path completo no disco.
	elif sys_kernel() == 'Windows':
		url = SetDataTor().set_windows_url()
		file = SetDataTor().set_filename_windows()
		dirCache = SetDataTor().set_cache_dir()    
		file = (f'{dirCache}\\{file}')             
		
	def __init__(self):
		pass

	def bar_custom(self, current, total, width=80):
		# https://pt.stackoverflow.com/questions/207887/como-imprimir-texto-na-mesma-linha-em-python
		# print('\033[K[>] Progresso: %d%% [%d / %d]MB ' % (progress, current, total), end='\r')
		#
		current = current / 1048576        # Converter bytes para MB
		total = total / 1048576            # Converter bytes para MB
		progress = (current / total) * 100 # Percentual

		if progress == '100':
			print('[>] Progresso: %d%% [%d / %d]MB ' % (progress, current, total))

		print('\033[K[>] Progresso: %d%% [%d / %d]MB ' % (progress, current, total), end='\r')


	def download_file(self):
		'''
		wget.download(url, out=None, bar=<function bar_adaptive at 0x7f7fdfed9d30>)
		wget.download(url, out=None, bar=bar_adaptive(current, total, width=80))
		'''
		import wget

		if os.path.isfile(self.file):
			yellow(f'Arquivo encontrado: {self.file}')
			return

		yellow(f'Baixando: {self.url}')
		yellow(f'Destino: {self.file}')
		try:
			wget.download(self.url, self.file, bar=self.bar_custom)
			print('OK ')
		except:
			print('\n')
			red('Falha no download')
			if os.path.isfile(self.file):
				os.remove(self.file)

	def unpack_file(self):
		# https://docs.python.org/3.3/library/tarfile.html
		yellow(f'Descomprimindo: {self.file}')
		yellow(f'Destino: {DirUnpackTor}')

		os.chdir(DirUnpackTor)
		tar = tarfile.open(self.file)
		tar.extractall()
		tar.close()

	def linux(self):
		'''
		Instalar o tor no linux.
		'''
		dir_temp_tor = (f'{DirUnpackTor}/tor-browser_en-US')
		list_files = os.listdir(dir_temp_tor)

		if os.path.isdir(DESTINATION_TOR) == False:
			yellow(f'Criando: {DESTINATION_TOR}')
			os.makedirs(DESTINATION_TOR)

		os.chdir(dir_temp_tor)

		# Mover arquivos descompactados para o diretório de instalação.
		for X in range(0, len(list_files)):
			OldFile = list_files[X]
			NewFile = (f'{DESTINATION_TOR}/{list_files[X]}')
			if (os.path.isdir(NewFile)) or (os.path.isfile(NewFile)):
				yellow(f'Encontrado: {NewFile}')
			else:
				yellow(f'Movendo: {OldFile} => {NewFile}')
				shutil.move(OldFile, NewFile)

		shutil. rmtree(DirUnpackTor)

		yellow(f'Criando atalho para execução em: {EXECUTABLE_TOR}')
		with open(EXECUTABLE_TOR, 'w') as f:
			f.write('#!/bin/sh\n')
			f.write(f'cd {DESTINATION_TOR}\n')
			f.write('{}/{}\n'.format(DESTINATION_TOR, 'start-tor-browser.desktop "$@"'))

		yellow(f'Executando: chdir {DESTINATION_TOR}')
		os.chdir(DESTINATION_TOR)
		os.chmod('start-tor-browser.desktop', 0o755)
		os.chmod(EXECUTABLE_TOR, 0o755)
		yellow('./{} --register-app'.format('start-tor-browser.desktop'))
		os.system('./{} --register-app'.format('start-tor-browser.desktop'))
		yellow('Use: torbrowser --help - para mais informações')
		os.system('torbrowser')

	def remove_torlinux(self):
		'''
		Desinstalar tor no Linux
		'''
		if os.path.isfile(DESKTOP_FILE) == True:
			yellow(f'Removendo: {DESKTOP_FILE}')
			os.remove(DESKTOP_FILE)

		if os.path.isfile(EXECUTABLE_TOR):
			yellow(f'Removendo: {EXECUTABLE_TOR}')
			os.remove(EXECUTABLE_TOR)

	def windows(self):
		'''
		Executa o instalador .exe do windows
		'''
		os.chdir(f"{self.dirCache}")
		os.system(self.file) # Executar o instalador

	def remove_torwindows(self):
		pass

	def install_tor(self):
		if sys_kernel() == 'Windows':
			self.download_file()
			self.windows()
		elif sys_kernel() == 'Linux':
			self.download_file()
			self.unpack_file()
			self.linux()	

	def remove_tor(self):
		yellow('Removendo torbrowser')
		if sys_kernel() == 'Windows':
			self.remove_torwindows()
		elif sys_kernel() == 'Linux':
			self.remove_torlinux()		


parser = argparse.ArgumentParser(description='Instala o Navegador Tor em sistemas Linux e Windows.')

parser.add_argument(
	'-v', '--version', 
	action='version', 
	version=(f"%(prog)s {__version__}")
	)

parser.add_argument(
	'-i', '--install',
	action='store_true', 
	help='Baixa e instala o Navegador Tor',
	)

parser.add_argument(
	'-r', '--remove',
	action='store_true', 
	help='Desinstala o Navegador Tor',
	)

args = parser.parse_args()

if args.install:
	ConfigTor().install_tor()
elif args.remove:
	ConfigTor().remove_tor()
else:
	print(f'Use: {os.path.basename(os.path.realpath(__file__))} --install|--remove|--version|--help')











