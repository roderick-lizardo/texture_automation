# Lint as: python3
"""This sample code is a direct and linear approach to
generating 3d hand renders with a blender scene:
1. Create a scene in Blender.
2. Import 3d Hand obect.
3. Import a random object.
4. Script the Hand to grab the object.
5. Load post-compositing nodes and randomize HDRI.
6. Output specified render passes.

"""

import csv
import sys
import logging
import random
import os
import json
import bpy

import hand_output_properties
import hand_grab_to_shape

logging.basicConfig(level=logging.INFO)

# Paths.
logging.info('Reading csv path')

import hand_output_properties as hEP

# Paths Constants
BASE_PATH = hEP.base_path
print("hEP.base_path")
print(hEP.base_path)
CSV_PATH = os.path.join(BASE_PATH, 'csv/')
MOD_PATH = os.path.join(BASE_PATH, 'models/')
TEXT_PATH = os.path.join(BASE_PATH, 'textures/')
BLEND_PATH = os.path.join(BASE_PATH, 'blend/')


def load():
  # Reading hand_scene_list.csv for order of operations,
  # this will be used for importing and data extraction.
  logging.info('Reading: CSV List.')
  hand_side_order = []
  upc_order = []
  hand_side_list = []
  hand_size_list = []
  hand_color_list = []
  obj_shape_list = []
  with open(CSV_PATH + 'hand_scene_list.csv', 'r') as csvfile:
    csvread = csv.reader(csvfile)
    for i, row in enumerate(csvread):
      if i == 0: continue
      upc = row[0]
      hand_side = row[2]
      hand_size = row[3]
      hand_color = row[4]
      obj_shape = row[5]
      hand_side_list.append(hand_side)
      hand_size_list.append(hand_size)
      hand_color_list.append(hand_color)
      upc_order.append(upc)
      obj_shape_list.append(obj_shape)

  logging.info('Creating blender scene.')
  # Blender Data Variables.
  d = bpy.data
  dOB = d.objects

  # Blender Operation Variables.
  o = bpy.ops
  imp_fbx = o.import_scene.fbx

  # Blender Context Variables.
  c = bpy.context
  view_layer = c.view_layer


  # Get current frame.
  frame_number = bpy.context.scene.frame_current
  logging.info('Confirming frame number: %s', str(frame_number))
  prod_id = upc_order[frame_number]
  # Read 3 lists. 1) product_list 2) hand_list.

  # Lists and Dictionary for the first list.
  logging.info('Creating a dictionary for upc to product name for bpy importing operations.')
  upc_to_product = {}
  upc_list = []
  with open(CSV_PATH + 'hand_product_list.csv', 'r') as csvfile:
    csvread = csv.reader(csvfile)
    for i, row in enumerate(csvread):
      if i == 0: continue
      upc = row[0]
      product = row[1]
      upc_to_product[upc] = product
      upc_list.append(upc)

  # Parse random variables to form a hand filename.
  logging.info('Parsing variables to create a hand.')
  current_upc = upc_order[frame_number]
  hand_side = hand_side_list[frame_number]
  hand_size = hand_size_list[frame_number]
  hand_color = hand_color_list[frame_number]
  logging.info('Hand side: %s', str(hand_side))
  logging.info('Hand size: %s', str(hand_size))
  logging.info('Hand color: %s', str(hand_color))
  ##############################################################################

  # Importing hand.

  ##############################################################################

  # Read CSV and get hand order from list
  # Object or no Object
  obj_no_obj_decision = obj_shape_list[frame_number]
  if obj_no_obj_decision == 'no_object':
    hand_no_obj_gesture_type = ['unique','pose']
    gesture = random.choice(hand_no_obj_gesture_type)
    if gesture == 'pose':
      hand = hand_side + '_' + str(hand_size) + '_no_object'
    else:
      hand = hand_side + '_' + str(hand_size)
  else:
    hand = hand_side + '_' + str(hand_size)
  logging.info('Generating hand: %s', str(hand))

  # Path to .blend file and appends/references collection.
  path_file = BLEND_PATH + 'hand_id/hands_inventory.blend\\Collection\\'
  o.wm.append(filename=hand, directory=path_file)

  # Add Texture for hand.
  # Select hand mesh and make active.
  hnd = dOB[hand+'_mesh']
  hnd.select_set(True)
  view_layer.objects.active = hnd
  bpy.context.object.active_material_index = 0

  # Select active material and matnodes.
  bpy.context.object.active_material.name = hand_side+'_'+str(hand_size) + '_material'
  hand_mat = bpy.data.materials[hand_side+'_'+str(hand_size)+'_material']
  hand_matnodes = hand_mat.node_tree.nodes

  # Load hand texture.
  hand_texture = TEXT_PATH+'hand_textures/'+str(hand_side)+ '_diffuse_' + str(hand_color)+'.jpg'
  load_img = bpy.data.images.load(hand_texture)
  hand_matnodes[str(hand_size)+'_diffuse'].image = load_img
  logging.info('!!!')
  logging.info('!!!')
  logging.info('!!!')
  logging.info('Texture has successfully been applied to the hand!')

  ##########################################################################

  # Importing sleeve.

  ##########################################################################
  sleeve_list = ['one']
  rand_sleeve = random.choice(sleeve_list)
  sleeve_asset = 'sleeve_'+str(rand_sleeve)
  sleeve = imp_fbx(filepath=MOD_PATH+'/clothes/'+str(sleeve_asset)+'.fbx')
  c.selected_objects[0].name = 'sleeve'
  bpy.ops.object.select_all(action='DESELECT')
  dOB['sleeve'].select_set(True)
  sleeve_mesh = dOB['sleeve']
  view_layer.objects.active = sleeve_mesh
  bpy.ops.object.constraint_add(type='COPY_LOCATION')

  # Snap Sleeve to locator
  bpy.context.object.constraints['Copy Location'].target = bpy.data.objects[hand+'_for_snapping']

  # Deselect to reset procedure.
  bpy.ops.object.select_all(action='DESELECT')
  sleeve_mesh.select_set(True)
  view_layer.objects.active = sleeve_mesh
  bpy.ops.object.constraint_add(type='COPY_ROTATION')
  bpy.context.object.constraints['Copy Rotation'].target = bpy.data.objects[hand+'_for_snapping']

  # Load Sleeve texture
  # Materials.
  bpy.context.object.active_material.name = sleeve_asset + '_material'
  sleeve_mat = bpy.data.materials[sleeve_asset + '_material']
  sleeve_matnodes = sleeve_mat.node_tree.nodes

  # Texture Name.
  rand_sleeve_color = random.randint(1,4)
  sleeve_texture = TEXT_PATH + 'clothes/'+ str(sleeve_asset) + '_' + str(rand_sleeve_color) + '.jpg'
  load_sleeve_img = bpy.data.images.load(sleeve_texture)
  sleeve_matnodes['Image Texture'].image = load_sleeve_img
  logging.info('!!!')
  logging.info('!!!')
  logging.info('!!!')
  logging.info('Texture has successfully been applied to the hand!')
  # Deselect to reset procedure.
  bpy.ops.object.select_all(action='DESELECT')

  # Apply hand assets to a new collection.
  bn = bpy.data.objects[hand + '_bn']
  bn.select_set(True)
  view_layer.objects.active = bn
  o.object.select_all(action='SELECT')
  o.object.move_to_collection(collection_index=1, is_new=True,
                              new_collection_name=hand_output_properties.task+'_hand')

  ##############################################################################

  # Importing product.

  ##############################################################################

  # Deselect.
  logging.info('Deselecting.')
  o.object.select_all(action='DESELECT')
  # Import Product.
  product = upc_to_product[prod_id]
  imp_fbx_name = MOD_PATH + '/products/' + str(product) + '.fbx'
  # Import fbx file.
  imp_fbx(filepath=imp_fbx_name)
  logging.info('Product has been imported: ' + str(product))

  # Rename object to product
  obj_name = bpy.context.selected_objects[0].name
  logging.info('Renaming %s to %s', str(obj_name), str(product))
  bpy.context.selected_objects[0].name = product

  # Add Texture to product.
  prod_obj = dOB[product]
  prod_obj.select_set(True)
  logging.info('Name of object selected: %s', str(product))
  view_layer.objects.active = prod_obj
  bpy.context.object.active_material_index = 0

  # Rename active material
  bpy.context.object.active_material.name = str(product) + '_material'
  mat = bpy.data.materials[product+'_material']
  logging.info('Material name is called: %s_material', str(product))
  matnodes = mat.node_tree.nodes
  product_texture = TEXT_PATH + 'products/' + str(product) + '_BaseColor.jpg'
  logging.info('Product texture path: %s', str(product_texture))
  load_product_img = bpy.data.images.load(product_texture)
  matnodes['Image Texture'].image = load_product_img
  logging.info('!!!')
  logging.info('!!!')
  logging.info('!!!')
  logging.info('Texture has successfully been applied to the object!')
  #############################################################################

  # Hand is grabbing product.

  #############################################################################
  logging.info('Hand is grabbing product.')
  logging.info('Choosing to grab top or grab side.')
  prod_width = dOB[product].dimensions[0]
  prod_depth = dOB[product].dimensions[1]
  prod_height = dOB[product].dimensions[2]
  obj = d.objects[product]
  index_assignment = 0
  loc_x = obj.dimensions[0] * random.uniform(.1,.3)
  loc_y = obj.location[1]
  loc_z = obj.dimensions[2]

  # List for fingers.
  ik_finger_controllers = ['index','middle','pinky','ring','thumb']
  ik_front_fingers = ['index','middle','pinky','ring']

  # Front fingers grab product
  finger_name = hand+'_ik_'

  # Grab list.
  grab = ['top','side']
  rand_grab = random.choice(grab)
  # Grab is either top or side. Currently just for left hand.
  random_slide_sideways = prod_depth * random.uniform(.5,.9)
  random_height = loc_z * random.uniform(.9,.8)
  if rand_grab == 'top':
    logging.info('I\'ve chosen top.')
    logging.info('Shape grab is: %s', str(obj_shape_list[frame_number]))

    # CYLINDER GRAB FROM TOP.
    if obj_shape_list[frame_number] == 'cylinder':
      logging.info('Grabbing cylinder')
      for ik_fing in ik_finger_controllers:
        dOB[finger_name+str(ik_fing)].location[2] = random_height
      dOB[finger_name+'index'].location[0] = 0.06839
      dOB[finger_name+'index'].location[1] = 0
      dOB[finger_name+'pinky'].location[1] = 0.060513
      dOB[finger_name+'ring'].location[1] = 0.055579
      dOB[finger_name+'middle'].location[1] = 0.040513
      dOB[finger_name+'thumb'].location[0] = 0
      dOB[finger_name+'thumb'].location[1] = 0
      logging.info('Height: %s', str(random_height))
      d.objects[hand+'_root'].location[0] = loc_x
      d.objects[hand+'_root'].location[1] = loc_y
      d.objects[hand+'_root'].location[2] = prod_height + random.uniform(-.03,0)
      dOB[hand+'_bn'].location[1] = dOB[hand+'_bn'].location[1] + random.uniform(-.4,-.003)


    # NO OBJECT HAND.
    # Unique gesture is a random hand pose that is out of the ordinary.
    elif obj_shape_list[frame_number] == 'no_object':
      if gesture == 'unique':
        logging.info('No object hand gesture: %s', str(gesture))
        rand_rotation = random.uniform(-1,1)
        logging.info('No object here.')
        finger_name = hand+'_ik_'
        middle_finger_loc_z = dOB[hand+'_ik_middle'].location[2]
        dOB[finger_name+'thumb'].location[0] = random.uniform(-0.02995,.2)
        dOB[finger_name+'thumb'].location[1] = random.uniform(0.028542,.03)
        dOB[finger_name+'thumb'].location[2] = middle_finger_loc_z + random.uniform(-.03,.03)
        for cont in ik_finger_controllers:
          dOB[finger_name+str(cont)].rotation_euler[1] = rand_rotation
        for ff in ik_front_fingers:
          dOB[finger_name+str(ff)].location[0] = dOB[finger_name+str(ff)].location[0] + random.uniform(-.001,.001)
          dOB[finger_name+str(ff)].location[1] = dOB[finger_name+str(ff)].location[1] + random.uniform(-0.001458,.001)
          dOB[finger_name+str(ff)].location[2] = dOB[finger_name+str(ff)].location[2] + random.uniform(-.050,.0150)
        dOB[finger_name+'pinky'].location[0] = random.uniform(-0.051739,-0.021739)
        dOB[finger_name+'index'].location[0] = random.uniform(0.10839,0.16839)
        dOB[hand+'_root'].location[1] = dOB[hand+'_root'].location[1] + random.uniform(-.01,.02)
        dOB[hand+'_root'].location[2] = dOB[hand+'_root'].location[2] + random.uniform(0,.01)
        dOB[hand+'_root'].rotation_euler[1] = dOB[hand+'_root'].rotation_euler[1] = rand_rotation

      else:
        logging.info('Gesture is: %s', str(gesture))
        bpy.ops.object.select_all(action='DESELECT')
        pose_bn = dOB[hand+'_bn']
        pose_bn.select_set(True)
        view_layer.objects.active = pose_bn
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        # Random pose index.
        rand_pose_index = random.randint(0,105)
        bpy.ops.poselib.apply_pose(pose_index=rand_pose_index)
        bpy.ops.object.mode_set(mode='OBJECT')

    # RECTANGLE TOP GRAB.
    else:
      hand_grab_to_shape.rectangle_grab()
      middle_finger_loc_z = dOB[hand+'_ik_middle'].location[2]
      dOB[finger_name + 'thumb'].location[0] = random_slide_sideways
      dOB[finger_name + 'thumb'].location[1] = 0
      dOB[finger_name + 'thumb'].location[2] = middle_finger_loc_z + random.uniform(-.03,.03)
      for ik_ctrl in ik_finger_controllers:
        dOB[finger_name+str(ik_ctrl)].location[2] = random_height
      for ik_front in ik_front_fingers:
        dOB[finger_name+str(ik_front)].location[1] = prod_depth

      logging.info('Height: %s', str(random_height))
      d.objects[hand+'_root'].location[0] = loc_x
      d.objects[hand+'_root'].location[1] = loc_y
      d.objects[hand+'_root'].location[2] = prod_height + random.uniform(-.03,.03)
      dOB[hand+'_root'].location[1] = dOB[hand+'_root'].location[1] + random.uniform(-.04,.04)
      dOB[hand+'_root'].location[2] = dOB[hand+'_root'].location[2] + random.uniform(0,.01)

    #Apply modified for mesh deform. This has not been fully investigated.
    #Select product and apply modifier.

    # Deselect.
    if obj_no_obj_decision == 'no_object':
      logging.info('No object to deform.')
    else:
      logging.info('Deselecting.')
      o.object.select_all(action='DESELECT')
      dOB[product].select_set(True)
      view_layer.objects.active = obj
      bpy.ops.object.modifier_add(type='MESH_DEFORM')
      bpy.context.object.modifiers['MeshDeform'].precision = 5
      bpy.context.object.modifiers['MeshDeform'].object = dOB[hand+'_mesh']
      bpy.context.object.modifiers['MeshDeform'].object = bpy.data.objects[hand+'_mesh']
      bpy.ops.object.meshdeform_bind(modifier='MeshDeform')

  #####################################################################################
  #
  #
  #  GRABBING SIDE OF PRODUCT.
  #
  #  Easy way is to just rotate the product, but that solution does not help with
  # human interaction when synthetic humans walk into a store and grab products.
  #####################################################################################
  else:
    logging.info('I\'m grabbing side.')
    logging.info('Shape grab is: %s', str(obj_shape_list[frame_number]))

    # CYLINDER GRAB FROM TOP.
    if obj_shape_list[frame_number] == 'cylinder':
      logging.info('Grabbing cylinder')
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].rotation_euler[1] = -1.57
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].location[2] = prod_height * random.uniform(.3,.7)
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].location[0] = 0
      dOB[finger_name+'index'].location[0] = 0.13839
      dOB[finger_name+'index'].location[1] = 0.028542
      dOB[finger_name+'index'].location[2] = .3285
      dOB[finger_name+'middle'].location[0] = 0.102685
      dOB[finger_name+'middle'].location[1] = .027862
      dOB[finger_name+'middle'].location[2] = .31256
      dOB[finger_name+'ring'].location[0] = 0.060677
      dOB[finger_name+'ring'].location[1] = 0.04241
      dOB[finger_name+'ring'].location[2] = .32121
      dOB[finger_name+'pinky'].location[0] = .027794
      dOB[finger_name+'pinky'].location[1] = .058069
      dOB[finger_name+'pinky'].location[2] = .34745
      dOB[finger_name+'thumb'].location[0] = .12179
      dOB[finger_name+'thumb'].location[1] = .006079
      dOB[finger_name+'thumb'].location[2] = .31182
      dOB[hand+'_root'].location[0] = .0189
      dOB[hand+'_root'].location[1] = .001048
      dOB[hand+'_root'].location[2] = .419
      dOB[hand+'_bn'].location[0] = 6.77935
      dOB[hand+'_bn'].location[1] = -9.3192
      dOB[hand+'_bn'].location[2] = -5.2303
      dOB[hand+'_ik_parent'].location[2] = 0.480365

    # NO OBJECT HAND.
    # Unique gesture is a random hand pose that is out of the ordinary.
    elif obj_shape_list[frame_number] == 'no_object':

      # Unique gesture side.
      if gesture == 'unique':
        dOB[hand+'_parent'].rotation_euler[1] = random.uniform(0,6.28)
        logging.info('No object hand gesture: %s', str(gesture))
        rand_rotation = random.uniform(-1,1)
        logging.info('No object here.')
        finger_name = hand+'_ik_'
        middle_finger_loc_z = dOB[hand+'_ik_middle'].location[2]
        dOB[finger_name+'thumb'].location[0] = dOB[finger_name+'thumb'].location[0]+random.uniform(-0.02995,.02)
        dOB[finger_name+'thumb'].location[1] = dOB[finger_name+'thumb'].location[1] + random.uniform(0.028542,.03)
        dOB[finger_name+'thumb'].location[2] = middle_finger_loc_z + random.uniform(-.03,.03)
        for ff in ik_front_fingers:
          dOB[finger_name+str(ff)].location[0] = dOB[finger_name+str(ff)].location[0] + random.uniform(.0015,.00191)
          dOB[finger_name+str(ff)].location[1] = dOB[finger_name+str(ff)].location[1] + random.uniform(-0.001458,.001)
          dOB[finger_name+str(ff)].location[2] = dOB[finger_name+str(ff)].location[2] + random.uniform(-.0150,-.05550)
        dOB[finger_name+'pinky'].location[0] = random.uniform(-0.051739,-0.021739)
        dOB[finger_name+'index'].location[0] = random.uniform(0.10839,0.16839)
        dOB[hand+'_root'].location[1] = dOB[hand+'_root'].location[1] + random.uniform(-.01,.02)
        dOB[hand+'_root'].location[2] = dOB[hand+'_root'].location[2] + random.uniform(0,.01)
        dOB[hand+'_root'].rotation_euler[1] = dOB[hand+'_root'].rotation_euler[1] = rand_rotation

      # No object Gesture Pose.
      else:
        logging.info('Gesture is: %s', str(gesture))
        dOB[hand+'_parent'].rotation_euler[1] = -1.57
        bpy.ops.object.select_all(action='DESELECT')
        pose_bn = dOB[hand+'_bn']
        pose_bn.select_set(True)
        view_layer.objects.active = pose_bn
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        # Random pose index.
        rand_pose_index = random.randint(0,105)
        bpy.ops.poselib.apply_pose(pose_index=rand_pose_index)
        bpy.ops.object.mode_set(mode='OBJECT')

    # RECTANGLE SIDE GRAB.
    else:
      bpy.ops.object.select_all(action='DESELECT')
      prod_height_variable = prod_height*random.uniform(.9,.3)
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].rotation_euler[1] = -1.57
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].location[2] = random.uniform(0,prod_height_variable)
      dOB[str(hand_side)+'_'+str(hand_size)+'_parent'].location[0] = 0 + random.uniform(-0.039,-.036)
      for ik_cont in ik_front_fingers:
        dOB[finger_name+ik_cont].location[1] = prod_depth

      # Thumb to box.
      dOB[finger_name+'thumb'].location[0] = prod_height * random.uniform(.7,.5)
      dOB[finger_name+'thumb'].location[1] = 0
      dOB[finger_name+'thumb'].location[2] = random.uniform(.367,0.317278)
      dOB[hand+'_ik_parent'].location[0] = random.uniform(0,.08)

  logging.info('Grab is complete.')

  ##########################################################################

  # Importing camera system.

  ##########################################################################
  # Create Camera system.
  logging.info('Creating camera system.')
  scene_name = 'camera_scene'
  bpy.ops.wm.append(filename=scene_name, directory=path_file)
  bpy.context.scene.camera = bpy.data.objects['Camera']

  # Lock cam_path and cam_track to center of wrist by taking
  # Applying locations to camera system: cam_track, and cam_path.
  # Add modifiers to both cam path and cam track.
  bpy.ops.object.select_all(action='DESELECT')
  dOB['cam_path'].select_set(True)
  cam_path_obj = dOB['cam_path']
  view_layer.objects.active = cam_path_obj
  bpy.ops.object.constraint_add(type='COPY_LOCATION')

  # Snap cam_path to locator.
  bpy.context.object.constraints['Copy Location'].target = bpy.data.objects[hand+'_for_cam_snapping']



  # cam track constraint.
  bpy.ops.object.select_all(action='DESELECT')
  dOB['cam_track'].select_set(True)
  cam_track_obj = dOB['cam_track']
  view_layer.objects.active = cam_track_obj
  bpy.ops.object.constraint_add(type='COPY_LOCATION')

  # Snap cam_track to locator.
  bpy.context.object.constraints['Copy Location'].target = bpy.data.objects[hand+'_for_cam_snapping']

  logging.info('Coordinates have been applied to the camera system.')

  # Pass index.
  dOB[hand + '_mesh'].pass_index = 1
  if obj_no_obj_decision == 'no_object':
    dOB[product].pass_index = 0
  else:
    dOB[product].pass_index = 1

def main():
  load()

if __name__ == '__main__':
  main()
