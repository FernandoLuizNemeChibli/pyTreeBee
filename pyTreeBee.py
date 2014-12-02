'''
Author: Fernando Luiz Neme Chibli
Name: pyTreeBee
Version: 0.6
License: GNU LGPL v2.1
'''

'''
Asgard Defense is the first game made with pyTreeBee.

Asgard Defense by Asgardian AGES is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/.

Asgard Defense v0.30 is available on http://goo.gl/JkKElS.
'''

import pygame, os,time
from pygame.locals import *

pygame.init()
pygame.mixer.init()

def treeBeeStart(tela_principal):
    while tela_principal.running:
        tela_principal.run()
        if tela_principal.storedlink:
            proxima_tela=tela_principal.storedlink.linkReply(tela_principal)
            tela_principal.storedlink=None
            tela_principal=proxima_tela

class entryBox(object):
    def __init__(self, font, string_entry, box_width, x , y, indentation=10):
        self.text=string_entry
        self.x=x
        self.y=y
        self.width=box_width
        self.font=font
        self.indentation=indentation

        self.digit_position=0
        
        self.bar=(0,0,0) # Black
        self.background=(255,255,255) # White
        self.color=(0,0,0) # Black
        self.bar_width=1 # How much smaller is the background rect?
        self.selected=False # You didn't selected it, did you?
        self.limit=1000001 # "It's over one million" - Freeza

    #-Getters-#
    def getString(self):
        return self.text

    #-Setters-#
    def setColors(self, bar_color, background_color, text_color):
        self.bar=bar_color
        self.background=background_color
        self.color=text_color
    def setBarColor(self, bar_color):
        self.bar=bar_color
    def setBackground(self, background_color):
        self.background=background_color
    def setBarWidth(self, bar_width):
        self.bar_width=bar_width
    def setTextColor(self, text_color):
        self.color=text_color
    def setLimit(self, char_limit):
        self.limit=char_limit

    #-Box "Blitter"-#
    def blitOn(self, screen):
        #width, font_height+indentation
        screen.fill( self.bar,pygame.Rect(self.x,self.y,self.width, (2*self.indentation)+self.font.get_height() ))
        #width-bar_width, font_height+indentation
        screen.fill( self.background,pygame.Rect(self.x+self.bar_width,self.y+self.bar_width,self.width-2*self.bar_width, (2*self.indentation)+self.font.get_height()-2*self.bar_width ))
        #text before the position plus a bar
        string_exibition=self.text[:self.digit_position]+'|'
        text_display=self.font.render(string_exibition,True,self.color)
        if text_display.get_width()>self.width-self.indentation: #if it get of the bounds, it displays focusing the position...
            #I think that I was drunk when I did all this... thing... I'm tired, lets sleep...
            screen.blit(text_display,(self.x+ self.width -self.indentation -text_display.get_width(),self.y+self.indentation))
            string_exibition2=self.text[self.digit_position:]
            text_display2=self.font.render(string_exibition2,True,self.color)
            screen.blit(text_display2,(self.x+self.width-self.indentation,self.y+self.indentation))
        else:
            text_display=self.font.render(string_exibition+self.text[self.digit_position:],True,self.color)
            screen.blit(text_display,(self.x+self.indentation,self.y+self.indentation))

    #-Selection Verifier-#
    def mouseSelect(self, event):
        if event.type == MOUSEBUTTONUP and event.button==1:
            x,y=event.pos
            if x>self.x and y>self.y and x< self.x+self.width and y < self.y+(2*self.indentation)+self.font.get_height()-2*self.bar_width:
                self.selected=True
            else:
                self.selected=False

    #-Text and Key Manipulator-#
    def keyPressed(self, event):
        if event.type == KEYDOWN:
            if event.key==K_DELETE and self.digit_position<len(self.text):
                self.text=self.text[:self.digit_position]+self.text[self.digit_position+1:]
            else:
                if event.key==K_BACKSPACE and self.digit_position>0:
                    self.text=self.text[:self.digit_position-1]+self.text[self.digit_position:]
                    self.digit_position-=1
                else:
                    if event.key==K_RIGHT and self.digit_position<len(self.text):
                        self.digit_position+=1
                    else:
                        if event.key==K_LEFT and self.digit_position>0:
                            self.digit_position-=1
                        else:
                            if event.key >= 32 and event.key <= 126 and len(self.text)<self.limit:
                                if pygame.key.get_mods() & KMOD_SHIFT or  pygame.key.get_mods() & KMOD_CAPS:
                                    self.text=self.text[:self.digit_position]+(chr(event.key).upper())+self.text[self.digit_position:]
                                else:
                                    self.text=self.text[:self.digit_position]+chr(event.key)+self.text[self.digit_position:]
                                self.digit_position+=1
    def keyControls(self, event):
        self.mouseSelect(event)
        if self.selected:
            self.keyPressed(event)
        return False

class linkedButton(object):
    def __init__(self, screen, font, text_vector, x,y ,rect, x_indentation, y_indentation, image=None):
        self.text=[text_vector]*3
        self.x=x
        self.y=y
        self.rect=[rect]*3
        if image!=None:
            self.image=[image]*3
            self.scale=[self.image[0].get_size()]*3
        else:
            self.image=[None]*3 
            self.scale=[(1,1)]*3
        
        self.bar_image=[None]*3
        self.bar_scale=[(1,1)]*3
        #scale = image resize
        self.bar=[(0,0,0)]*3
        self.bar_size=[(1,1)]*3
        #size = rect size
        
        
        self.background=[(255,255,255)]*3
        self.color=[(0,0,0)]*3
        
        self.font=[font]*3
        self.x_indentation=[x_indentation]*3
        self.y_indentation=[y_indentation]*3
        self.state=0
        self.link=screen
        self.actived=False
        self.hovered_sound=None
        self.selected_sound=None
        self.wait_sound=0
    def buttonTurnOff(self):
        self.actived=False
    def moveTo(self, location):
        for r in self.rect:
            r.x=location[0]
            r.y=location[1]

    def setSelect_Text(self, text, font=None):
        self.text[0]=text
        if font!=None:
            self.font[0]=font
    def setSelect_Font(self, font):
        self.font[0]=font
    def setSelect_Indentation(self, indent):
        self.x_indentation[0]=indent[0]
        self.y_indentation[0]=indent[1]
    def setButton(self, font, text_vector, rect, x_indentation, y_indentation):
        self.text[0]=text_vector
        self.rect[0]=rect
        self.font[0]=font
        self.x_indentation[0]=x_indentation
        self.y_indentation[0]=y_indentation
    def setColors(self, bar_color, background_color, text_color):
        self.bar[0]=bar_color
        self.background[0]=background_color
        self.color[0]=text_color
    def setBarColor(self, bar_color):
        self.bar[0]=bar_color
    def setBackground(self, background_color):
        self.background[0]=background_color
    def setTextColor(self, text_color):
        self.color[0]=text_color
    def setBarSize(self, bar_size):
        self.bar_size[0]=bar_size
    def setImage(self, image):
        self.image[0]=image
    def setScale(self, size):
        self.scale[0]=size
    def setBarImage(self, image):
        self.bar_image[0]=image
    def setBarScale(self, size):
        self.bar_scale[0]=size
    def setHover_Sound(self,sound):
        self.hovered_sound=sound
    def setHover_Text(self, text, font=None):
        self.text[1]=text
        if font!=None:
            self.font[1]=font
    def setHover_Font(self, font):
        self.font[1]=font
    def setHover_Indentation(self, indent):
        self.x_indentation[1]=indent[0]
        self.y_indentation[1]=indent[1]
    def setHover(self, font, text_vector, rect, x_indentation, y_indentation):
        self.text[1]=text_vector
        self.rect[1]=rect
        self.font[1]=font
        self.x_indentation[1]=x_indentation
        self.y_indentation[1]=y_indentation
    def setHover_Colors(self, bar_color, background_color, text_color):
        self.bar[1]=bar_color
        self.background[1]=background_color
        self.color[1]=text_color
    def setHover_BarSize(self, bar_size):
        self.bar_size[1]=bar_size
    def setHover_Image(self, image):
        self.image[1]=image
    def setHover_Scale(self, size):
        self.scale[1]=size
    def setHover_BarImage(self, image):
        self.bar_image[1]=image
    def setHover_BarScale(self, size):
        self.bar_scale[1]=size
    def setSelect_Sound(self,sound):
        self.selected_sound=sound
    def setSelect_Text(self, text, font=None):
        self.text[2]=text
        if font!=None:
            self.font[2]=font
    def setSelect_Font(self, font):
        self.font[2]=font
    def setSelect_Indentation(self, indent):
        self.x_indentation[2]=indent[0]
        self.y_indentation[2]=indent[1]
    def setSelect(self, font, text_vector, rect, x_indentation, y_indentation):
        self.text[2]=text_vector
        self.rect[2]=rect
        self.font[2]=font
        self.x_indentation[2]=x_indentation
        self.y_indentation[2]=y_indentation
    def setSelect_Colors(self, bar_color, background_color, text_color):
        self.bar[2]=bar_color
        self.background[2]=background_color
        self.color[2]=text_color
    def setAll_BarColor(self, bar_color):
        self.bar=[bar_color]*3
    def setAll_Background(self, background_color):
        self.background=[background_color]*3
    def setAll_TextColor(self, text_color):
        self.color=[text_color]*3
    def setAll_Text(self, text, font=None):
        self.text=[text]*3
        if font!=None:
            self.font=[font]*3
    def setAll_Font(self, font):
        self.font=[font]*3
    def setAll_Indentation(self, indent):
        self.x_indentation=[indent[0]]*3
        self.y_indentation=[indent[1]]*3
    def setAll_BarSize(self, bar_size):
        self.bar_size=[bar_size]*3
    def setAll_Image(self, image):
        self.image=[image]*3
    def setAll_Scale(self, size):
        self.scale=[size]*3
    def setAll_BarImage(self, image):
        self.bar_image=[image]*3
    def setAll_BarScale(self, size):
        self.bar_scale=[size]*3
    def setAll_Sound(self,sound):
        self.hovered_sound=sound
        self.selected_sound=sound
    def setEach_Sound(self,sound1,sound2):
        self.hovered_sound=sound1
        self.selected_sound=sound2
    def setEach_Text(self, text1,text2,text3):
        self.text=[text1,text2,text3]
    def setEach_Image(self, img1,img2,img3):
        self.image=[img1,img2,img3]
        self.scale=[img1.get_size(),img2.get_size(),img3.get_size()]
    def setEach_Scale(self, size,size_hover,size_select):
        self.scale=[size,size_hover,size_select]
    def setEach_BarSize(self, size,size_hover,size_select):
        self.bar_size=[size,size_hover,size_select]
    def setSound_Time(self,time=-1):
        self.wait_sound=time
    def blitOn(self, screen):
        try:
            if self.bar_image[self.state]==None:
                screen.fill( self.bar[self.state], pygame.Rect(self.x+self.rect[self.state].x,self.y+self.rect[self.state].y,self.rect[self.state].w,self.rect[self.state].h))
            else:
                scaled_bar = pygame.transform.scale(self.bar_image[self.state],self.bar_scale[self.state])
                screen.blit( scaled_bar[self.state], (self.x+self.rect[self.state].x,self.y+self.rect[self.state].y))
            if self.image[self.state]==None:
                screen.fill( self.background[self.state],pygame.Rect(self.x+self.rect[self.state].x+self.bar_size[self.state][0],self.y+self.rect[self.state].y+self.bar_size[self.state][1],self.rect[self.state].width-2*self.bar_size[self.state][0], self.rect[self.state].height-2*self.bar_size[self.state][1]))
            else:
                scaled_image = pygame.transform.scale( self.image[self.state],self.scale[self.state])
                screen.blit( scaled_image,(self.x+self.rect[self.state].x+self.bar_size[self.state][0],self.y+self.rect[self.state].y+self.bar_size[self.state][1]))
        except:
            pass
        for n in range(len(self.text[self.state])):
            text_display=self.font[self.state].render(self.text[self.state][n],True,self.color[self.state])
            screen.blit(text_display,(self.x+self.rect[self.state].x+self.x_indentation[self.state],self.y+self.rect[self.state].y+self.y_indentation[self.state]+n*self.font[self.state].get_height()))
    def mouseColide(self,event):
        x,y=event.pos
        if x>self.x+self.rect[self.state].x and y>self.y+self.rect[self.state].y and x< self.x+self.rect[self.state].x+self.rect[self.state].width and y < self.y+self.rect[self.state].y+self.rect[self.state].height:
            return True
        else:
            return False
    def keyControls(self, event):#, refresh_itens= None):
        reply=False
        if event.type == MOUSEBUTTONDOWN and event.button==1:
            if self.mouseColide(event):
                if self.state!=2 and self.selected_sound!=None:
                    self.selected_sound.play()
                    if self.wait_sound>0:
                        time.sleep(self.wait_sound)
                    if self.wait_sound<0:
                        time.sleep(self.selected_sound.get_length())
                self.state=2
                self.actived=True
        if event.type == MOUSEMOTION and self.actived==False:
            if self.mouseColide(event):
                if self.state!=1 and self.hovered_sound!=None:
                    self.hovered_sound.play()
                self.state=1
            else:
                self.state=0
        if event.type == MOUSEBUTTONUP and event.button==1:
            self.actived=False
            if self.mouseColide(event):
                reply = self.link
                '''
                try:
                    self.link.refresh(refresh_itens)
                except:
                    pass'''
        return reply

class accelGame(object):
    def __init__(self, fps):
        self.fps=fps
    def linkReply(self,prevscr):
        prevscr.fps=self.fps
        return prevscr

class volumeControl(object):
    def __init__(self, how_much):
        self.amount=how_much
    def linkReply(self, prevscr):
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + self.amount)
        return prevscr

class renderVolume(object):
    def __init__(self, fonte,cor,x,y,diferenciador=1):
        self.font=fonte
        self.color=cor
        self.x=x
        self.y=y
        self.unit=diferenciador
    def blitOn(self,scr):
        scr.blit(self.font.render(str(int(pygame.mixer.music.get_volume()*self.unit)),True,self.color),(self.x,self.y))
    def keyControls(self,event):pass

class directWriter(object):
    def __init__(self, render, x,y):
        self.render=render
        self.x=x
        self.y=y
    def blitOn(self,scr):
        scr.blit(self.render,(self.x,self.y))
    def keyControls(self,event):pass

class accelKey(object):
    def __init__(self,fps,key):
        self.link=accelGame(fps)
        self.key=key
    def keyControls(self,event):
        retorno=False
        if event.type==KEYUP:
            if event.key==self.key:
                retorno=self.link
        return retorno
    def blitOn(self,scr):pass

class linkedMusic(object):
    def __init__(self, link, music, repeat, start_time):
        self.link=link
        self.music=music
        self.repeat=repeat
        self.start_time=start_time
    def linkReply(self,prevscr):
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(self.music)
        except:
            print "can't load music"
        try:
            pygame.mixer.music.play(self.repeat,self.start_time)
        except:
            print "can't play music"
        self.link.stored_music=self.music
        return self.link

class sendItens(object):
    def __init__(self):
        self.actived=True
        self.itens=[]
        self.destiny=None
    def refresh(self, refresh):
        self.itens=[]
        for item in refresh[0]:
            self.itens.append(item.text)
        self.destiny=refresh[1]
    def linkReply(self,tela_principal):
        tela_principal.addItem(self.destiny)
        tela_principal.itens[len(tela_principal.itens)-1].receive(self.itens)
        return tela_principal
        

class submitGroup(object):
    #destiny=None
    #sendItens era InnerClass aqui mas nao deu certo
    def __init__(self, destiny,(font, text_vector, rect, x_indentation, y_indentation), *itens):
        self.destiny=destiny
        self.itens=list(itens)
        self.sendbutton=linkedButton(sendItens(), font, text_vector, rect, x_indentation, y_indentation)
    def addItem(self,item):
        self.itens.append(item)
    def keyControls(self, event):
        for item in self.itens:
            item.keyControls(event)
        return self.sendbutton.keyControls(event,(self.itens,self.destiny))
    def blitOn(self,scr):
        for item in self.itens:
            item.blitOn(scr)
        self.sendbutton.blitOn(scr)
        

class basicReceive(object):
    def __init__(self, x,y, font, color):
        self.itens=[]
        self.x=x
        self.y=y
        self.font=font
        self.color=color
    def receive(self,itens):
        self.itens=itens
    def blitOn(self, scr):
        text_display=self.font.render("Sent Data:",True,self.color)
        scr.blit(text_display,(self.x,self.y-self.font.get_height()))
        for n in range(len(self.itens)):
            text_display=self.font.render(str(self.itens[n]),True,self.color)
            scr.blit(text_display,(self.x,self.y+n*self.font.get_height()))
    def keyControls(self, event):
        pass

class osWeblink(object):
    def __init__(self, link):
        self.link=link
    def linkReply(self, previousscreen):
        os.system("START "+str(self.link))
        return previousscreen

class osCommand(object):
    def __init__(self, *cmd):
        self.cmd_vector=list(cmd)
    def linkReply(self, previousscreen):
        for cmd in self.cmd_vector: os.system(str(cmd))
        return previousscreen

class itemCounter(object):
    def __init__(self,scr,link,count):
        self.scr=scr
        self.link=link
        self.count=count
    def keyControls(self,event):pass
    def blitOn(self,scr):
        if self.count==0:
            self.scr.linkcalled=self.link

class moveObject(object):
    def __init__(self, origem,item, pos_ini, destino, velocidade):
        self.item=item
        self.origem=origem
        self.pos_ini=pos_ini
        self.destino=destino
        self.step=(((destino[0]-pos_ini[0])/velocidade),((destino[1]-pos_ini[1])/velocidade))
    def keyControls(self,event):
        return False
    def blitOn(self,scr):
        try:
            if self.destino[0]!=self.item.x:
                self.item.x+=self.step[0]
            if self.destino[1]!=self.item.y:
                self.item.y+=self.step[1]
            if self.destino[0]==self.item.x and self.destino[1]==self.item.y:
                self.origem.count-=1
                self=None            
        except:
            try:
                if self.destino[0]!=self.item.pos[0]:
                    self.item.pos[0]+=self.step[0]
                if self.destino[1]!=self.item.pos[1]:
                    self.item.pos[1]+=self.step[1]
                if self.destino[0]==self.item.pos[0] and self.destino[1]==self.item.pos[1]:
                    self.origem.count-=1
                    self=None
            except:
                pass

def fadeIn(scr,link, *itens):
    origem=itemCounter(scr,link,len(itens))
    scr.addItem(origem)
    for item in itens:
        try:
            scr.addItem(moveObject(origem,item[0], (item[0].x,item[0].y), item[1], item[2]))
        except:
            try:
                scr.addItem(moveObject(origem,item[0], (item[0].pos[0],item[0].pos[0]), item[1], item[2]))#item,posicao inicial,destino,velocidade
            except:
                pass

class dynamicScreen(object):
    def __init__(self, size, fps, color, *itens):
        self.size=size
        self.fps=fps
        self.color=color
        self.image=None
        self.imagepos=(0,0)
        self.itens=list(itens)
        self.screenpos=(0,0)
        self.storedlink=None
        self.linkcalled=False
        self.running=True
        self.full=False
        self.music=False
        self.stored_music=False
        self.startpos=None
        self.repeat=None
        self.stopmusic=False
        self.title=None
        self.title_fps=False
    def setMusic(self, music,repeat,startpos, stop=True):
        self.music=music
        self.repeat=repeat
        self.startpos=startpos
        self.stopmusic=stop
    def setFULLSCREEN(self):
        self.full=True
    def linkReply(self, previousscreen):
        return self
    def setImage(self, image, imagepos):
        self.image=image
        self.imagepos=imagepos
    def setColor(self, color):
        self.color=color
    def addItem(self,*itens):
        for item in itens:
            self.itens.append(item)
        #print len(self.itens)
        #print type(item)
    def setTitle(self,title,fps=False):
        self.title=title
        self.title_fps=fps
    def run(self):
        if self.full:
            infoObject = pygame.display.Info()
            self.size=(infoObject.current_w, infoObject.current_h)
            display = pygame.display.set_mode(self.size,FULLSCREEN)
        else:
            display = pygame.display.set_mode(self.size)
        fpsClock=pygame.time.Clock()
        self.linkcalled=False
        if self.music:# and pygame.mixer.music.get_busy()==False
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.play(self.repeat,self.startpos)
        if self.title: pygame.display.set_caption(self.title)
        while self.running and self.linkcalled==False:
            if self.title==None: pygame.display.set_caption(str(int(fpsClock.get_fps()))+":"+str(self.fps))
            elif self.title_fps==True: pygame.display.set_caption(str(self.title+" FPS "+int(fpsClock.get_fps()))+":"+str(self.fps))
            for event in pygame.event.get():
                if event.type==QUIT:
                    self.storedlink=None
                    self.running=False
                for i in range(len(self.itens)):
                    
                    try:
                        #time.sleep( (len(self.itens)-i)/100)
                        self.linkcalled=self.itens[i].keyControls(event)
                        if self.linkcalled!=None and self.linkcalled!=False:
                            break
                    except:
                        #print 'keyControls() error on screen "'+str(self.title)+'", self.itens[ '+str(i)+' ]'
                        pass
            display.fill(self.color)
            if self.image!=None:
                try:
                    display.blit(self.image,self.imagepos)
                except:
                    print 'background error'
            for i in range(len(self.itens)):
                try:
                    self.itens[i].blitOn(display)
                except:
                    #print 'blitOn() error on screen "'+str(self.title)+'", self.itens[ '+str(i)+' ]'
                    pass
            pygame.display.update()
            fpsClock.tick(self.fps)
        if self.linkcalled!=None and self.linkcalled!=False:
            self.storedlink=self.linkcalled
        if self.stopmusic:
            pygame.mixer.music.stop()
'''
frame_atual=0
class extraControls(object):
    def __init__(self,tela):
        self.tela=tela
        self.frame_skip=1
    def blitOn(self,screen):
        global frame_atual
        frame_atual+=self.frame_skip
    def keyControls(self,event):
        return False

tela3=dynamicScreen((800,600),60,(90,90,90))
tela2=dynamicScreen((800,600),60,(90,90,90),linkedButton(osWeblink("www.google.com"),pygame.font.SysFont("arial",12),["google"],100,200,pygame.Rect(0,0,100,100),0,0))
tela1=dynamicScreen((800,600),60,(90,90,90),linkedButton(tela2,pygame.font.SysFont("arial",12),["tela2"],100,100,pygame.Rect(0,0,100,100),0,0),linkedButton(tela3,pygame.font.SysFont("arial",12),["tela3"],200,100,pygame.Rect(0,0,100,100),0,0))
tela2.addItem(linkedButton(tela1,pygame.font.SysFont("arial",12),["tela1"],100,100,pygame.Rect(0,0,100,100),0,0))
tela3.addItem(linkedButton(tela1,pygame.font.SysFont("arial",12),["tela1"],100,100,pygame.Rect(0,0,100,100),0,0))
#tela1.setMusic("Five Armies.mp3",-1,0.0,False)
tela1.addItem(extraControls(tela1))
#tela2.setMusic("Teller of the Tales.mp3",-1,0.0,True)
treeBeeStart(tela1)
pygame.quit()
'''
