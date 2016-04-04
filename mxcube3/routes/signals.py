import logging, json, inspect
from mxcube3 import socketio
from mxcube3 import app as mxcube
import time

@socketio.on('connect', namespace='/hwr')
def connect():
    # this is needed to create the namespace, and the actual connection
    # to the server, but we don't need to do anything more
    pass

collectSignals = ['collectStarted', 'collectOscillationStarted', 'collectOscillationFailed', 'collectOscillationFinished','collectEnded', 'testSignal', 'collectReady', 'warning']
queueSignals = ['queue_execution_finished', 'queue_paused', 'queue_stopped', 'testSignal', 'warning'] #'centringAllowed',
microdiffSignals = ['centringInvalid','newAutomaticCentringPoint','centringStarted','centringAccepted','centringMoving','centringFailed','centringSuccessful','progressMessage','centringSnapshots', 'warning', 'positionChanged', 'phiMotorStateChanged','phiyMotorStateChanged','phizMotorStateChanged', 'sampxMotorStateChanged', 'sampyMotorStateChanged', 'minidiffStateChanged'] #'diffractometerMoved', 

okSignals = ['Successful', 'Finished', 'finished','Ended', 'Accepted'] 
failedSignals = ['Failed','Invalid']
progressSignals = ['Started', 'Ready', 'paused', 'stopped', 'Moving', 'progress', 'centringAllowed']
warnSignals = ['warning']

def signalCallback(*args, **kwargs):
    logging.getLogger("HWR").debug(kwargs) 
    logging.getLogger("HWR").debug(args) 
    sender = str(kwargs['sender'].__class__).split('.')[0]
    signal = kwargs['signal']
    result = 0
    #parse signal to integer
    #1: ~nothing done; 2: ok, 3: failed, 4: warning
    for sig in progressSignals:
        if sig in signal:
            result = 1
    for sig in okSignals:
        if sig in signal:
            result = 2
    for sig in failedSignals:
        if sig in signal:
            result = 3
    for sig in warnSignals:
        if sig in signal:
            result = 4
        
    # NOT SURE ABOUT THIS ONE

    lastQueueNode = mxcube.queue.lastQueueNode

    if len(args) >0:
        if args[0] in queueSignals:
            msg = {'data':'no data', 'signal': args[0],'sender':sender, 'queueId':lastQueueNode['id'], 'sample' :lastQueueNode['sample'] ,'state':result}
        else:
            if signal == 'minidiffStateChanged':
                aux = {}
                for p in mxcube.diffractometer.savedCentredPos:
                    aux.update({p['posId']:p})
                msg = {'data': aux, 'signal': signal,'sender':sender, 'queueId':lastQueueNode['id'],'sample' :lastQueueNode['sample'] ,'state':result}
            else:
                msg = {'data':json.dumps(args), 'signal': signal,'sender':sender, 'queueId':lastQueueNode['id'],'sample' :lastQueueNode['sample'] ,'state':result}
    else:
        if signal == 'minidiffStateChanged':
            aux = {}
            for p in mxcube.diffractometer.savedCentredPos:
                aux.update({p['posId']:p})
            msg = {'data': aux, 'signal': signal,'sender':sender, 'queueId':lastQueueNode['id'],'sample' :lastQueueNode['sample'] ,'state':result}
        else:
            msg = {'data':'no data', 'signal': signal,'sender':sender, 'queueId':lastQueueNode['id'],'sample' :lastQueueNode['sample'] ,'state':result}
            msg = {'data':json.dumps(args), 'signal': signal,'sender':sender, 'queueId':lastQueueNode['id'],'sample' :lastQueueNode['sample'] ,'state':result}
    
    logging.getLogger("HWR").debug('Signal callback. origin: "%s",signal: "%s", queueId: "%s", result: "%d"' %(sender,signal, lastQueueNode['id'], result))
    try:
        socketio.emit('hwr_record',msg , namespace='/hwr')
        if '<class ' in sender : sender = sender[7:]
        msg = { "message": sender +':'+signal, "severity": 'INFO', "timestamp":time.asctime(), "logger":'HWR', "stack_trace":'' }
        socketio.emit('log_record', msg, namespace='/logging')

    except:
        logging.getLogger("HWR").error('error creating the message')
