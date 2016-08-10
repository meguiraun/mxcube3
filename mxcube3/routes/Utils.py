from mxcube3 import app as mxcube
from mxcube3 import socketio
from flask import Response, session
from functools import wraps
import logging
import jsonpickle
import redis


def _proposal_id(session):
    try:
        return int(session["loginInfo"]["loginRes"]["Proposal"]["number"])
    except (KeyError, TypeError, ValueError):
        return None


def save_queue(session, redis=redis.Redis()):
    proposal_id = _proposal_id(session)
    if proposal_id is not None:
        redis.set("mxcube:queue:%d" % proposal_id, jsonpickle.encode(mxcube.queue))


def new_queue(serialized_queue=None):
    if not serialized_queue:
        serialized_queue = mxcube.empty_queue
    queue = jsonpickle.decode(serialized_queue)
    import Queue
    Queue.init_signals(queue)
    return queue


def get_queue(session, redis=redis.Redis()):
    proposal_id = _proposal_id(session)
    if proposal_id is not None:
        serialized_queue = redis.get("mxcube:queue:%d" % proposal_id)
    else:
        serialized_queue = None

    return new_queue(serialized_queue)


def get_light_state_and_intensity():
    ret = dict()

    for light in ('BackLight', 'FrontLight'):
        item_role = light.lower()

        hwobj = mxcube.diffractometer.getObjectByRole(item_role)

        if hasattr(hwobj, "getActuatorState"):
            switch_state = 1 if hwobj.getActuatorState() == 'in' else 0
        else:
            hwobj_switch = mxcube.diffractometer.getObjectByRole(light + 'Switch')
            switch_state = 1 if hwobj_switch.getActuatorState() == 'in' else 0

        ret.update({light: {"Status": hwobj.getState(), "position": hwobj.getPosition()},
                    light + 'Switch': {"Status": switch_state, "position": 0}
                    })

    return ret


def get_movable_state_and_position(item_name):
    item_role = item_name.lower()
    ret = dict()

    try:
        if 'light' in item_role:
            # handle all *light* items in the same way;
            # this returns more than needed, but it doesn't
            # matter
            return get_light_state_and_intensity()

        hwobj = mxcube.diffractometer.getObjectByRole(item_role)

        if hwobj is None:
            logging.getLogger("HWR").error('[UTILS.GET_MOVABLE_STATE_AND_POSITION] No movable with role "%s"' % item_role)
        else:
            if hasattr(hwobj, "getCurrentPositionName"):
                # a motor similar to zoom
                pos_name = hwobj.getCurrentPositionName()
                if pos_name:
                    pos = hwobj.predefinedPositions[pos_name]
                else:
                    pos = None
                return {item_name: {"Status": hwobj.getState(), "position": pos}}
            else:
		pos = hwobj.getPosition()
		try:
		    pos = round(pos, 2)
		except:
		    pass
                return {item_name: {'Status': hwobj.getState(), 'position': pos}}
    except Exception:
        logging.getLogger('HWR').exception('[UTILS.GET_MOVABLE_STATE_AND_POSITION] could not get item "%s"' % item_name)


def get_centring_motors_info():
    # the centring motors are: ["phi", "focus", "phiz", "phiy", "zoom", "sampx", "sampy", "kappa", "kappa_phi"]
    ret = dict()
    for name in mxcube.diffractometer.centring_motors_list:
        motor_info = get_movable_state_and_position(name)
        if motor_info and motor_info[name]['position'] is not None:
            ret.update(motor_info)
    return ret

def my_execute_entry(self, entry):
    import queue_entry as qe
    import time
    import random
    from mxcube3 import app as mxcube
    self.emit('centringAllowed', (False, ))
    self._current_queue_entries.append(entry)
    print "executing on my waaaaay madarikatuak"
    print entry
    if isinstance(entry, qe.DataCollectionQueueEntry):
        time.sleep(1)
        # mxcube.collect.emit('collectOscillationStarted')
        # time.sleep(2)
        #logging.getLogger('HWR').info('[COLLECT] collectOscillationStarted')
        mxcube.collect.emit('collectStarted')
        time.sleep(2)
        # mxcube.collect.emit('collectOscillationFinished')
        # time.sleep(2)
        foo = ['collectOscillationFinished', 'collectOscillationFailed', 'warning']
        mxcube.collect.emit(random.choice(foo))
    elif isinstance(entry, qe.CharacterisationGroupQueueEntry):
        logging.getLogger('HWR').info('[QUEUE] Executing CharacterisationGroupQueueEntry entry: %s' %entry)
        time.sleep(1)
        char = entry.get_data_model()
        reference_image_collection = char.reference_image_collection
        # Trick to make sure that the reference collection has a sample.
        reference_image_collection._parent = char.get_parent()
        gid = entry.get_data_model().get_parent().lims_group_id
        reference_image_collection.lims_group_id = gid
        # Enqueue the reference collection and the characterisation routine.
        dc_qe = qe.DataCollectionQueueEntry(entry.get_view(),
                                            reference_image_collection,
                                            view_set_queue_entry=False)
        dc_qe.set_enabled(True)
        entry.enqueue(dc_qe)
        entry.dc_qe = dc_qe

        if char.run_characterisation:
            char_qe = qe.CharacterisationQueueEntry(entry.get_view(), char,
                                                 view_set_queue_entry=False)
            char_qe.set_enabled(True)
            entry.enqueue(char_qe)
            entry.char_qe = char_qe

        mxcube.collect.emit('collectOscillationStarted')
        #logging.getLogger('HWR').info('[COLLECT] collectOscillationStarted')
        for child in entry._queue_entry_list:
            mxcube.queue.queue_hwobj.execute_entry(child)
#            child.execute()#child)
        time.sleep(2)
        foo = ['collectOscillationFinished', 'collectOscillationFailed', 'warning']
        mxcube.collect.emit(random.choice(foo))
        logging.getLogger('HWR').info('[QUEUE] Finished Executing CharacterisationGroupQueueEntry entry: %s' %entry)

    elif isinstance(entry, qe.CharacterisationQueueEntry):
        logging.getLogger('HWR').info('[QUEUE] Executing CharacterisationQueueEntry entry: %s' %entry)

        time.sleep(1)
        mxcube.collect.emit('collectOscillationStarted')
        log = logging.getLogger("user_level_log")
        log.info("Characterising, please wait ...")
        time.sleep(2)
        log.info("Characterisation completed.")
        foo = ['collectOscillationFinished', 'collectOscillationFailed', 'warning']
        mxcube.collect.emit(random.choice(foo))
        logging.getLogger('HWR').info('[QUEUE] Finished CharacterisationQueueEntry entry: %s' %entry)
        logging.getLogger('HWR').info('[QUEUE] Creating DataCollection')

        char = entry.get_data_model()

        acq_parameters = mxcube.beamline.get_default_acquisition_parameters()
        params = {
                'first_image': acq_parameters.first_image,
                'num_images': acq_parameters.num_images,
                'osc_start': acq_parameters.osc_start,
                'osc_range' : acq_parameters.osc_range,
                'kappa' : acq_parameters.kappa,
                'kappa_phi' : acq_parameters.kappa_phi,
                'overlap' : acq_parameters.overlap,
                'exp_time' : acq_parameters.exp_time,
                'num_passes' : acq_parameters.num_passes,
                'resolution' : acq_parameters.resolution,
                'energy' : acq_parameters.energy,
                'transmission' : acq_parameters.transmission,
                'shutterless' : acq_parameters.shutterless,
                'detector_mode' : acq_parameters.detector_mode,
                'inverse_beam' : False,
                'take_dark_current' : True,
                'skip_existing_images' : False,
                'take_snapshots' : True
                }
        params['path'] = char.characterisation_parameters.path_template.directory
        params['prefix'] = 'DiffPlan'
#        params['point'] = mxcube.diffractometer.save
        import queue_model_objects_v1 as qmo
        colNode = qmo.DataCollection()
        colEntry = qe.DataCollectionQueueEntry()
        from HardwareRepository.BaseHardwareObjects import Null as Mock #mock import Mock
        colEntry._view = Mock()
        #colEntry.set_queue_controller(qm)
        colEntry._set_background_color = Mock()

        taskNode1 = qmo.TaskGroup()
        task1Entry = qe.TaskGroupQueueEntry()
        task1Entry.set_data_model(taskNode1)

        colNode.acquisitions[0].acquisition_parameters.set_from_dict(params)
        import os
        colNode.acquisitions[0].path_template.directory = os.path.join(mxcube.session.get_base_image_directory(), params['path'])
        colNode.acquisitions[0].path_template.run_number = mxcube.queue.get_next_run_number(char.characterisation_parameters.path_template)

        colNode.acquisitions[0].path_template.base_prefix = params['prefix']
        if mxcube.queue.check_for_path_collisions(colNode.acquisitions[0].path_template):
            logging.getLogger('HWR').exception('[QUEUE] datacollection could not be added to sample: Data Collision')
            return Response(status=409)


        char_cpos = char.reference_image_collection.acquisitions[0].acquisition_parameters.centred_position.as_dict()
        log.info(char_cpos)
        for cpos in mxcube.diffractometer.savedCentredPos:
            log.info(cpos)
            char_cpos.pop('zoom')
            if char_cpos == cpos['motorPositions']:
                log.info(char_cpos)
                params['point'] = str(cpos['posId'])
                log.info("POINT FOUND")
        
        colNode.acquisitions[0].acquisition_parameters.centred_position = char.reference_image_collection.acquisitions[0].acquisition_parameters.centred_position

        colEntry.set_data_model(colNode)
        colEntry.set_enabled(True)
        colNode.set_enabled(True)
        colNode.mikels_flag = 'AutoGenerated'
        node = char._parent._parent
        node_id = node._node_id  # mxcube.queue.get_node(int(id))
        aux_entry = mxcube.queue.queue_hwobj.get_entry_with_model(node)

        task1Id = mxcube.queue.add_child_at_id(node_id, taskNode1)
        aux_entry.enqueue(task1Entry)

        newNode = mxcube.queue.add_child_at_id(task1Id, colNode)  # add_child does not return id!
        task1Entry.enqueue(colEntry)
        logging.getLogger('HWR').info('[QUEUE] DataCollection Created: %s' %colEntry)

        save_queue(session)

        logging.getLogger('HWR').info('[QUEUE] datacollection added to sample')
        data_json = {'QueueId': colNode._node_id, 'Type': 'DataCollection'}
        if mxcube.diffractometer.use_sc:    # use sample changer
            sampleID = str(mxcube.queue.get_node(node_id).location[0])+':'+str(mxcube.queue.get_node(node_id).location[1])
        else:
            sampleID = str(mxcube.queue.get_node(node_id).location[1])

        msg = {'sampleQueueID': node_id, 'sampleID': sampleID, 'task': data_json, 'params': params}
        log.info("Diffraction plan added to the queue: %s" % str(msg))

        socketio.emit('add_task', msg, namespace='/hwr')
    elif isinstance(entry, qe.SampleCentringQueueEntry):
        time.sleep(1)
        mxcube.diffractometer.emit('centringStarted')
        time.sleep(2)
        foo = ['centringSuccessful', 'centringFailed', 'warning']
        mxcube.diffractometer.emit(random.choice(foo))
        #mxcube.diffractometer.emit('centringSuccessful')

    #logging.getLogger('HWR').info('Calling execute on my execute_entry method')
    #logging.getLogger('HWR').info('Calling execute on: ' + str(entry))
    #logging.getLogger('HWR').info('Using model: ' + str(entry.get_data_model()))

    # for child in entry._queue_entry_list:
    #     self.my_execute_entry(child)

    self._current_queue_entries.remove(entry)
    print "executing on my waaaaay madarikatuak finished"


def __execute_entry(self, entry):
    print "my execute_entry"
    from routes.Queue import queue, last_queue_node
    import logging
    logging.getLogger('queue_exec').info('Executing mxcube3 customized entry')

    node = entry.get_data_model()
    nodeId = node._node_id
    parentId = int(node.get_parent()._node_id)
    #if this is a sample, parentId will be '0'
    if parentId == 0:  # Sample... 0 is your father...
        parentId = nodeId
    last_queue_node.update({'id': nodeId, 'sample': queue[parentId]['SampleId']})
    print "enabling....", entry
    #entry.set_enabled(True)
    if not entry.is_enabled() or self._is_stopped:
        logging.getLogger('queue_exec').info('Cannot excute entry: ' + str(nodeId) + '. Entry not enabled or stopped.')
        return
    self.emit('centringAllowed', (False, ))
    self._current_queue_entries.append(entry)
    logging.getLogger('queue_exec').info('Calling execute on: ' + str(entry))
    logging.getLogger('queue_exec').info('Using model: ' + str(entry.get_data_model()))
    if self.is_paused():
        logging.getLogger('user_level_log').info('Queue paused, waiting ...')
        entry.get_view().setText(1, 'Queue paused, waiting')
    self.wait_for_pause_event()
    try:
        # Procedure to be done before main implmentation
        # of task.
        entry.pre_execute()
        entry.execute()

        for child in entry._queue_entry_list:
            self.__execute_entry(child)

    except queue_entry.QueueSkippEntryException:
        # Queue entry, failed, skipp.
        pass
    except (queue_entry.QueueAbortedException, Exception) as ex:
        # Queue entry was aborted in a controlled, way.
        # or in the exception case:
        # Definetly not good state, but call post_execute
        # in anyways, there might be code that cleans up things
        # done in _pre_execute or before the exception in _execute.
        entry.post_execute()
        entry.handle_exception(ex)
        raise ex
    else:
        entry.post_execute()

    self._current_queue_entries.remove(entry)
