import numpy as np
import matplotlib.gridspec as gridspec
from scipy import sparse
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import math as mt
from stimulus import *
from myintegrator import *
import cProfile
import json

# this is the transfer function 
def phi(x,theta,uc):
	myresult=nu*(x-theta)
	myresult[x<theta]=0.
	myresult[x>uc]=nu*(uc-theta)
	return myresult

def mytau(x): #time scale function synapses
	myresult=(1e50)*np.ones(len(x))
	myresult[x>thres]=tau_learning
	#print x>thres
	#print x
	#myresult=(1e8)*(1.+np.tanh(-50.*(x-thres)))+tau_learning
	#print myresult
	return myresult

def winf(x_hist):
	pre_u=phi(x_hist[0],theta,uc)
	post_u=phi(x_hist[-1],theta,uc)
	#parameters
	n=len(pre_u)
	return (wmax/4.)*np.outer((np.ones(n)+np.tanh(a_post*(post_u-b_post))),(np.ones(n)+np.tanh(a_pre*(pre_u-b_pre))))

#function for the field
#x_hist is the 'historic' of the x during the delay period the zero is the oldest and the -1 is the newest

def tauWinv(x_hist):
	pre_u=x_hist[0]
	post_u=x_hist[-1]
	#return  np.add.outer(1/mytau(post_u),1/mytau(pre_u))
	return tau_learning*np.outer(1./mytau(post_u),1./mytau(pre_u))


def field(t,x_hist,W):
	field_u=(1/tau)*(mystim.stim(t)+W.dot(phi(x_hist[-1],theta,uc))-x_hist[-1]-w_inh*np.dot(r1_matrix,phi(x_hist[-1],theta,uc)))
	field_w=np.multiply(tauWinv(x_hist),(-W+winf(x_hist)))
	return field_u,field_w




#This are a the parameters of the simulation
#-------------------------------------------------------------------------------------
#------------------------Parameter Model----------------------------------------------
#-------------------------------------------------------------------------------------


#open parameters of the model
n=10 #n pop
delay=15.3 #multilpl:es of 9!
tau=10.   #timescale of populations
w_i=2.
nu=1.
theta=0.
uc=1.
wmax=2.5
thres=0.6
#parameters stimulation
dt=0.5
lagStim=500.


amp=10.
delta=15.3
period=40.
times=240

bf=10.
xf=0.7

a_post=bf
b_post=xf
a_pre=bf
b_pre=xf
tau_learning=400.




w_inh=w_i/n
r1_matrix=np.ones((n,n))
patterns=np.eye(n)
mystim=stimulus(patterns,lagStim,delta,period,times)
mystim.inten=amp
#integrato
npts=int(np.floor(delay/dt)+1)         # points delay
tmax=times*(lagStim+n*(period+delta))+40



#-------------------------------------------------------
#-------------------stimulation Network------------------
#--------------------------------------------------------

wsum=2.0
delta=10.
period=19.
amp_dc=-1.
amp=3.2-amp_dc
times=50
mystim=stimulus(patterns,lagStim,delta,period,times)
mystim.inten=amp
mystim.shuffle=True
mystim.amp_dc=amp_dc
tmax=times*(lagStim+n*(period+delta))+2000
tmax_long=tmax
#initial conditions
x0=0.01*np.ones((npts,n))
W0=[(wsum/n)*np.ones((n,n)) for i in range(npts)]
theintegrator=myintegrator(delay,dt,n,tmax)
theintegrator.fast=False

u,Wdiag,Woffdiag,connectivity,W01,t=theintegrator.DDE_Norm_additive(field,x0,W0)




#retrieval
amp=0.
times=300
mystim=stimulus(patterns,lagStim,delta,period,times)
mystim.inten=amp
mystim.amp_dc=0.
tmax=500
#initial conditions
x0=np.zeros((npts,n))
x0[:,0]=1.
W0=[connectivity[-1] for i in range(npts)]
theintegrator=myintegrator(delay,dt,n,tmax)
theintegrator.fast=False
u_ret,Wdiag_ret,Woffdiag_ret,connectivity_ret,W01_ret,t_ret=theintegrator.DDE_Norm_additive(field,x0,W0)


#-------------------------------------------------------------------------------------
#----------------Plotting--------------------------------------------------------------
#---------------------------------------------------------------------------------------

rc={'axes.labelsize': 32, 'font.size': 30, 'legend.fontsize': 25, 'axes.titlesize': 35}
plt.rcParams.update(**rc)
plt.rcParams['image.cmap'] = 'jet'
colormap = plt.cm.Accent

fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(2, 3)
gs.update(wspace=0.3,hspace=0.43)
gs0 = gridspec.GridSpec(2, 2)
gs0.update(wspace=0.1,hspace=0.1,left=0.67,right=0.91,top=0.88,bottom=0.56)
ax1 = plt.subplot(gs[0,0])
ax2 = plt.subplot(gs[0,1])
ax3a = plt.subplot(gs0[0,0])
ax3b = plt.subplot(gs0[0,1])
ax3c = plt.subplot(gs0[1,0])
ax3d = plt.subplot(gs0[1,1])
ax4 = plt.subplot(gs[1,0])
ax5 = plt.subplot(gs[1,1])
ax6 = plt.subplot(gs[1,2])


mystim.inten=.1
ax1.set_prop_cycle(plt.cycler('color',[colormap(i) for i in np.linspace(0, 0.9,n)]))
ax1.plot(t,phi(u[:,:],theta,uc),lw=3)
elstim=np.array([sum(mystim.stim(x)) for x in t])
ax1.plot(t,elstim,'k',lw=3)
ax1.fill_between(t,np.zeros(len(t)),elstim,alpha=0.5,edgecolor='k', facecolor='darkgrey')
ax1.set_xlim([12000,16000])
ax1.set_yticks([0.5,1])
ax1.set_xticks([12000,14000,16000])
ax1.set_xticklabels(['12','14','16'])
ax1.set_ylim([0,1.2])
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Rate')
ax1.set_title('(A)',y=1.04)

###dynamics synapses

for i in range(10):
		ax2.plot(t,connectivity[:,i,i],'c',lw=3)
for i in range(0,9):
		ax2.plot(t,connectivity[:,i+1,i],'y',lw=3)
for i in range(8):
		ax2.plot(t,connectivity[:,i+2,i],'g',lw=3)
for i in range(9):
		ax2.plot(t,connectivity[:,i,i+1],'r',lw=3)
for i in range(8):
		ax2.plot(t,connectivity[:,i,i+2],'b',lw=3)
#plt.xlim([0,tmax_long])
ax2.set_xticks([0,10000,20000,30000,40000])
ax2.set_yticks([0,1.,2])
ax2.set_xlim([0,40000])
ax2.set_ylim([0,2.1])
ax2.set_xticklabels([0,10,20,30,40])
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Synaptic Weights')
ax2.set_title('(B)',y=1.04)





vmax=2.
ax3a.matshow(connectivity[0,:,:],vmin=0,vmax=vmax)
ax3a.set_title('(C)',y=1.08,x=1.06)
ax3a.set_xticks([])
ax3a.set_yticks([])
ax3b.matshow(connectivity[int(tmax_long/(3*dt)),:,:],vmin=0,vmax=vmax)
ax3b.set_xticks([])
ax3b.set_yticks([])
ax3c.matshow(connectivity[int((2*tmax_long)/(3*dt)),:,:],vmin=0,vmax=vmax)
ax3c.set_xticks([])
ax3c.set_yticks([])
ax3d.matshow(connectivity[int(tmax_long/dt),:,:],vmin=0,vmax=vmax)
ax3d.set_xticks([])
ax3d.set_yticks([])
sm = plt.cm.ScalarMappable(cmap=plt.cm.jet, norm=plt.Normalize(vmin=0., vmax=vmax))
# fake up the array of the scalar mappable. Urgh...
sm._A = []
cax = fig.add_axes([0.92, 0.56, 0.02, 0.325]) # [left, bottom, width, height] 
myticks=[0.0,1,2]
cbar=fig.colorbar(sm, cax=cax,ticks=myticks,alpha=1.)
cbar.ax.tick_params(labelsize=30) 

#ax3.set_prop_cycle(plt.cycler('color',[colormap(i) for i in np.linspace(0, 0.9,n)]))
#ax3.plot(t_ret,phi(u_ret[:,:],theta,uc),lw=3)
#ax3.set_ylim([0,1.2])
#ax3.set_xlim([0,500])
#ax3.set_yticks([0,0.4,0.8,1.2])
#ax3.set_xlabel('Time (ms)')
#ax3.set_ylabel('Rate')

## Dynamics 
mystim.inten=.1
ax4.set_prop_cycle(plt.cycler('color',[colormap(i) for i in np.linspace(0, 0.9,n)]))
ax4.plot(t,phi(u[:,:],theta,uc),lw=3)
elstim=np.array([sum(mystim.stim(x)) for x in t])
ax4.plot(t,elstim,'k',lw=3)
ax4.fill_between(t,np.zeros(len(t)),elstim,alpha=0.5,edgecolor='k', facecolor='darkgrey')
ax4.set_ylim([0,1.2])
ax4.set_xlim([0,400])
ax4.set_yticks([0,0.5,1.])
ax4.set_xticks([0,200,400])
ax4.set_xticklabels([0,.2,.4])
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Rate')


ax5.set_prop_cycle(plt.cycler('color',[colormap(i) for i in np.linspace(0, 0.9,n)]))
ax5.plot(t,phi(u[:,:],theta,uc),lw=3)
ax5.plot(t,elstim,'k',lw=3)
ax5.fill_between(t,np.zeros(len(t)),elstim,alpha=0.5,edgecolor='k', facecolor='darkgrey')
ax5.set_ylim([0,1.2])
time_plot=10*(lagStim+n*(period+delta))
ax5.set_xlim([time_plot,time_plot+400])
ax5.set_xticks([time_plot,time_plot+200,time_plot+400])
ax5.set_xticklabels([time_plot*1e-3,(time_plot+200)*1e-3,(time_plot+400)*1e-3])
ax5.set_yticks([])
ax5.set_xlabel('Time (s)')
ax5.set_title('(D)',y=1.04)


ax6.set_prop_cycle(plt.cycler('color',[colormap(i) for i in np.linspace(0, 0.9,n)]))
ax6.plot(t,phi(u[:,:],theta,uc),lw=3)
ax6.plot(t,elstim,'k',lw=3)
ax6.fill_between(t,np.zeros(len(t)),elstim,alpha=0.5,edgecolor='k', facecolor='darkgrey')
ax6.set_ylim([0,1.2])
time_plot=30*(lagStim+n*(period+delta))
ax6.set_xlim([time_plot,time_plot+400])
ax6.set_xticks([time_plot,time_plot+200,time_plot+400])
ax6.set_xticklabels([time_plot*1e-3,(time_plot+200)*1e-3,(time_plot+400)*1e-3])
ax6.set_yticks([])
ax6.set_xlabel('Time (s)')


plt.savefig('fig6SM.pdf',transparent=True, bbox_inches='tight')
plt.close()



