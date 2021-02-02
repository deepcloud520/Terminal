'''
TERMINAL CORE
'''
import pygame as pg
import xml.etree.ElementTree as ET
import random as r
import queue
from terlocals import *

class screenIO:
    def __init__(self,maxline=30):
        self.history=[]
        self.maxline=maxline
    def flush(self):
        if len(self.history)>=self.maxline:
            self.history=self.history[0:self.maxline]
    def write(self,strs):
        line=list(filter(lambda x:True if x=='' else False,strs.split('\n')))
        if len(line)<=1:
            if len(self.history)==0:
                self.history.append(strs)
            else:
                self.history[-1]+=strs
        elif len(line)>2:
            self.writelines(line)
    def writelines(self,lsts):
        self.history.extend(lsts)
        self.flush()
    def readlines(self,num=0):
        if num==0:
            return self.history
        if num<len(self.history):
            return self.history[0:num]
        return []
    def read(self,bits=0):
        if bits>0:
            g=self.readlines()
            if bits<len(g):
                return g[bits]
            return ''
        else:
            return '\n'.join(self.history)
    def __str__(self):
        return self.read()

class NetWork:
    def __init__(self,fsfile):
        self.file=fsfile
        self.tree=ET.parse(fsfile)
        # load all
        self.network=[]
        for child in self.tree.getroot():
            self.network.append(OS(child))
    def save(self):
        self.tree.write(self.file)

class FileHandler:
    def  __init__(self,file):
        pass
    def write(self):
        pass
    def read(self):
        pass
    def writelines(self):
        pass
    def readlines(self):
        pass
    def close(self):
        pass
def debug(xml):
    for c in xml:
        print(c.tag,c.attrib['name'],c)
        debug(c)
class FileSystem:
    def __init__(self,XML):
        self.tree=XML
        self.cwd=['/']
    def getcwd(self):
        # return ['/']+'/'.join(self.cwd[1:])
        return self.cwd
    def setcwd(self,cwd):
        self.cwd=cwd
    def cd(self,nextpath):
        if not nextpath:
            return
        if nextpath[0]=='..':
            if len(self.getcwd())>1:self.setcwd(self.getcwd()[:-1])
            return
        c=self._getnode(self.getcwd())
        for child in c:
            if child.attrib['name']==nextpath[0] and child.tag=='folder':
                self.cwd.append(child.attrib['name'])
                # run self
                self.cd(nextpath[1:])
                break
        else:
            raise TerminalError('Folder not Found!')
    def _getnode(self,filedir):
        c=self.tree
        flag=False
        #if filedir[0]=='/':filedir=filedir[1:]
        for dr in filedir:
            for f in c:
                flag=False
                if f.get('name')==dr:
                    c=f
                    flag=True
                    break
            if not flag:
                raise TerminalError('File Not Found!')
        return c
    def exist(self,filedir):
        try:
            _getnode(self.abspath(filedir))
            return True
        except TerminalError:
            return False
    def remove(self,filedir):
        p=self.abspath(filedir)
        c=self._getnode(p)
        last=self._getnode(p[:-1])
        if c.tag=='file':
            last.remove(c)
    def isfile(self,filedir):
        try:
            c=self._getnode(self.abspath(filedir))
            if c.tag=='file':return True
            return False
        except TerminalError:
            return False
    def isdir(self,filedir):
        try:
            c=self._getnode(self.abspath(filedir))
            if c.tag=='folder':return True
            return False
        except TerminalError:
            return False
    def abspath(self,filedir):
        if filedir[0]=='/':
            # abs path
            return filedir
        if isinstance(filedir,str):
            return self.cwd+[filedir]
        return self.cwd+filedir
    def creatrefile(self,filedir):
        pass
    def rename(self,filedir):
        pass
    def listdir(self,filedir):
        '''listdir(filedir) >> [[file,..],[folder,..]]'''
        c=self._getnode(self.abspath(filedir))
        file=[]
        folder=[]
        if c.tag=='folder':
            for child in c:
                if child.tag=='file':
                    file.append(child.attrib['name'])
                elif child.tag=='folder':
                    folder.append(child.attrib['name'])
        elif c.tag=='filesystem':
            # Can't access root
            raise TerminalError('cannot access filesystem root.')
        else:
            raise TerminalError('input a folder,not file.')
        return [file,folder]
    def dir2list(self,strings):
        return strings.split('/')
    def list2dir(self,filedir):
        return '/'+'/'.join(filedir[1:])

class Process:
    def __init__(self,func):
        self.func=func
        self.memsave={}
        self.__alive=True
    def get_alive(self):
        return self.__alive
    def set_alive(self,varbool):
        self.__alive=varbool
    def run(self,*args,**kwargs):
        ret=self.func(self.memsave,*args,**kwargs)
        if ret==0:
            self.__alive=False
            return 0
        try:
            if isinstance(ret,dict):
                self.memsave.update(ret)
        except:
            print(ret)
            raise TypeError('must a dict return')
        
class OS:
    def __init__(self,init_XMLcode):
        self.kwrun={}
        self.memory={}
        self.historywarp=screenIO()
        self.inline_register()
        self.fsys=FileSystem(init_XMLcode.find('filesystem'))
        self.ip=init_XMLcode.attrib['ip']
    def inline_register(self):
        @self.inlinecommand('ps')
        def ps(m,obj,pid,*args):
            obj.historywarp.write('------------\n')
            for k,i in obj.memory.items():
                obj.historywarp.write(str(k)+'\t'+i[0].func.__name__+'\n')
            obj.historywarp.write('------------\n')
            return 0
        @self.inlinecommand('kill')
        def kill(m,obj,pid,*args):
            ret=obj.kill_byself(int(args[0]))
            if not ret:
                obj.historywarp.write('failed:kill failed\n')
            obj.historywarp.write('kill success\n')
            return 0
        @self.inlinecommand('rm')
        def remove(m,obj,pid,*args):
            if not m:
                # First Run
                if len(args)>1:
                    print('error:only a arg',obj.abspath(file),file=obj.historywarp)
                    return 0
                q=queue.Queue()
                dirline=obj.fsys.dir2list(args[0])
                if obj.fsys.isfile(dirline):
                    q.put(args[0])
                
                elif obj.fsys.isdir(dirline):
                    for item in obj.fsys.listdir(dirline)[0]:
                        q.put(dirline+[item])
                
                elif args[0]=='*':
                    # TRADITIONAL POWER
                    for item in obj.fsys.listdir(obj.fsys.getcwd())[0]:
                        q.put(item)
                return {'all':q}
            try:
                q=m['all']
                if not q.empty():
                    file=q.get()
                    if not file:return 0
                    obj.fsys.remove(file)
                    obj.historywarp.write('done:'+obj.fsys.list2dir(obj.fsys.abspath(file))+'\n')
                else:
                    return 0
            except TerminalError:
                # remove fail
                obj.historywarp.write('fail: '+obj.fsys.list2dir(obj.fsys.abspath(file))+'\n')
        @self.inlinecommand('cd')
        def cd(m,obj,pid,*args):
            if len(args)>1 or len(args)==0:
                obj.historywarp.write('failed:args only 1\n')
                return 0
            try:
                obj.fsys.cd(obj.fsys.dir2list(args[0]))
            except TerminalError:
                obj.historywarp.write('failed:No such as '+args[0]+'\n')
            return 0
        @self.inlinecommand('ls')
        def ls(m,obj,pid,*args):
            if len(args)>0:
                obj.historywarp.write('failed:not args\n')
                return 0
            file,dirs=obj.fsys.listdir(obj.fsys.getcwd())
            obj.historywarp.writelines(file)
            obj.historywarp.writelines(dirs)
            obj.historywarp.write('\n')
            return 0
    def newprocess(self,func,*args):
        rnum=r.randint(1,10000)
        while rnum in self.memory:
            rnum=r.randint(1,10000)
        # update to memory
        self.memory.update({rnum:[Process(func),*args]})
    
    def reg_command(self,name,func):
        self.kwrun.update({name:func})
    
    def update_all(self):
        remove_list=[]
        for k,i in self.memory.items():
            runnable=i[0]
            # is dead
            if not runnable.get_alive():
                remove_list.append(k)
                continue
            # start!
            r=runnable.run(self,k,*i[1:])
        for pid in remove_list:
            self.kill_bypid(pid)
    
    def inlinecommand(self,name):
        def warp(func):
            # register first
            self.reg_command(name,func)
            def run(*args,**kwargs):
                ret=func(self,*args,**kwargs)
                return ret
            return run
        return warp
    
    def kill_byself(self,pid):
        # for running-func in self.memory
        '''
        for k,i in self.memory.items():
            if i==func:
                # found one
                return self.kill_bypid(k)
        return -1
        '''
        try:
            self.memory[pid][0].set_alive(False)
            return True
        except KeyError:
            return False
    
    def kill_bypid(self,pid):
        if pid in self.memory:
            self.memory.pop(pid)
            return 0
        return -1
    
    def shellrun(self,strs):
        if not strs:return
        lparse=strs.split()
        cmd=lparse[0]
        if cmd in self.kwrun:
            self.newprocess(self.kwrun[cmd],*lparse[1:])
        else:
            self.historywarp.write('\"'+cmd+'" is not a command\n')

if __name__=='__main__':
    t=NetWork('loadacc/network.xml')
    ter1=t.network[0]
    while True:
        c=input(ter1.fsys.list2dir(ter1.fsys.getcwd())+':->')
        ter1.shellrun(c)
        ter1.update_all()
        print(ter1.historywarp)