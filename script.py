import bpy
import mathutils
from math import atan2, sqrt, radians ,degrees

# 清空场景
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    

def set_simple_color(obj, color=(1,1,1,1)):
    """为物体快速设置纯色材质（RGBA格式，数值范围0-1）"""
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"{obj.name}_Color")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color

def set_right_handed_rotation(obj):
    obj.rotation_mode = 'XYZ'

# 创建底盘（BasePlate）
def create_base_plate():
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.5, depth=0.56, vertices=3,
        location=(0, 0, 0.28)
    )
    base = bpy.context.active_object
    base.name = "BasePlate"
    set_right_handed_rotation(base)
    rot_constraint = base.constraints.new(type='LIMIT_ROTATION')
    rot_constraint.use_limit_x = True
    rot_constraint.use_limit_y = True
    rot_constraint.use_limit_z = False
    rot_constraint.owner_space = 'WORLD'
    loc_constraint = base.constraints.new(type='LIMIT_LOCATION')
    loc_constraint.use_min_x = True
    loc_constraint.use_max_x = True
    loc_constraint.use_min_y = True
    loc_constraint.use_max_y = True
    loc_constraint.min_x = 0
    loc_constraint.max_x = 0
    loc_constraint.min_y = 0
    loc_constraint.max_y = 0
    loc_constraint.owner_space = 'WORLD'
    set_simple_color(base, (0.8, 0.2, 0.2, 1))
    base.hide_viewport = False
    print(f"BasePlate: 局部={base.location}, 世界={base.matrix_world.translation}")
    return base

# 创建立柱（VerticalColumn）
def create_vertical_column(base):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    column = bpy.context.active_object
    column.name = "VerticalColumn"
    column.scale = (0.065, 0.065, 1.6)
    set_right_handed_rotation(column)
    column.parent = base
    column.matrix_parent_inverse = base.matrix_world.inverted()
    column.location = (0, 0, 1.36)
    bpy.context.view_layer.update()
    set_simple_color(column, (0.2, 0.3, 0.8, 1))
    #column.hide_viewport = False
    #print(f"VerticalColumn: 局部={column.location}, 世界={column.matrix_world.translation}")
    return column

# 创建滑块（Slider）
def create_slider(column):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    slider = bpy.context.active_object
    slider.name = "Slider"
    slider.scale = (0.02, 0.06, 0.08)
    set_right_handed_rotation(slider)
    slider.parent = column
    slider.matrix_parent_inverse = column.matrix_world.inverted()
    slider.location = (0.03, 0, 1.38)
    bpy.context.view_layer.update()
    constraint = slider.constraints.new(type='LIMIT_LOCATION')
    constraint.use_min_x = True
    constraint.use_max_x = True
    constraint.use_min_y = True
    constraint.use_max_y = True
    constraint.use_min_z = True
    constraint.use_max_z = True
    constraint.min_x = 0.03
    constraint.max_x = 0.03
    constraint.min_y = 0
    constraint.max_y = 0
    constraint.min_z = 0.6
    constraint.max_z = 2.12
    constraint.owner_space = 'LOCAL'
    set_simple_color(slider, (0.3, 0.8, 0.2, 1))
    slider.hide_viewport = False
    print(f"Slider: 局部={slider.location}, 世界={slider.matrix_world.translation}")
    return slider

# 创建目标球体（Ball）
def create_target_ball():
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.3, segments=8, ring_count=8,
        location=(2, 2, 2)
    )
    ball = bpy.context.active_object
    ball.name = "Ball"
    set_simple_color(ball, (0.9, 0.8, 0.1, 1))
    ball.hide_viewport = False
    print(f"Ball: 局部={ball.location}, 世界={ball.matrix_world.translation}")
    return ball

def create_end_hand(slider):
    # 创建一个六边柱体作为 EndHand
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02, depth=1.38, vertices=6, location=(0, 0, 0)
    )
    end_hand = bpy.context.active_object
    end_hand.name = "EndHand"

    # 移动顶点让底部对齐原点（Z轴 -0.69，柱体中心点下移）
    bpy.context.view_layer.objects.active = end_hand
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, 0.69))
    bpy.ops.object.mode_set(mode='OBJECT')

    # 保留当前世界矩阵
    world_matrix = end_hand.matrix_world.copy()

    # 设置为 slider 的子物体，并恢复位置
    end_hand.parent = slider
    end_hand.matrix_parent_inverse = slider.matrix_world.inverted()
    end_hand.matrix_world = world_matrix

    # 现在原点在底部了，可以贴在 slider 顶部
    # 如果 slider 高度是 1.38（EndHand 的高度），就设置 Z=0
    # 若 slider 是 1.0 高度，就用 slider 顶部高度来设置
    end_hand.location = (0.01 + 0.143, 0, 1.38)  # 

    # 设置旋转方向（你已有函数）
    set_right_handed_rotation(end_hand)

    # 限制旋转
    constraint = end_hand.constraints.new(type='LIMIT_ROTATION')
    constraint.use_limit_x = True
    constraint.use_limit_y = True
    constraint.use_limit_z = True
    constraint.min_x = radians(-120)
    constraint.max_x = radians(120)
    constraint.owner_space = 'LOCAL'

    # 设置颜色
    set_simple_color(end_hand, (0.7, 0.2, 0.9, 1))

    end_hand.hide_viewport = False
    print(f"EndHand: 局部={end_hand.location}, 世界={end_hand.matrix_world.translation}")
    return end_hand
    
    
def move_to_target(base, slider, end_hand, ball):
    target_pos = ball.matrix_world.translation

    # 获取 EndHand 的底部世界坐标
    endhand_base_world = end_hand.matrix_world @ mathutils.Vector((0, 0, 0))
    vec = target_pos - endhand_base_world

    # Base 朝向目标 (绕 Z 轴旋转)
    base_angle = atan2(vec.y, vec.x)
    base.rotation_euler.z = base_angle + radians(90)  # 加90度因为初始方向是 X+

    bpy.context.view_layer.update()

    # 将目标位置转换到 Base 局部坐标
    base_inv = base.matrix_world.inverted()
    target_local = base_inv @ target_pos

    # 计算水平距离和垂直距离
    horizontal_dist = sqrt(target_local.x**2 + target_local.y**2)
    vertical_dist = target_pos.z - endhand_base_world.z

    # 计算绕 X 轴的旋转角度
    angle = atan2(horizontal_dist, vertical_dist)

    # 设置 EndHand 绕 X 轴旋转
    end_hand.rotation_euler.x = angle

    bpy.context.view_layer.update()

    # 计算 EndHand 末端在世界坐标的位置
    endhand_length = 1.38  # EndHand 的长度
    endhand_tip_local = mathutils.Vector((0, 0, endhand_length))  # 修改点：沿 Z 轴指向末端
    tip_world_pos = end_hand.matrix_world @ endhand_tip_local

    # 可视化：把 3D 光标移动到末端
    bpy.context.scene.cursor.location = tip_world_pos

    # 计算末端与目标的 Z 差异，并调整 Slider 高度
    offset_z = target_pos.z - tip_world_pos.z
    slider.location.z += offset_z
    slider.location.z = max(0.6, min(2.12, slider.location.z))  # 限制范围

    bpy.context.view_layer.update()

    # 误差输出
    final_tip_pos = end_hand.matrix_world @ endhand_tip_local
    dx, dy, dz = (target_pos - final_tip_pos)
    error = sqrt(dx**2 + dy**2 + dz**2)
    print(f"[误差] {error:.4f}m，角度 {degrees(angle):.2f}°")

    return error

# 场景更新处理函数
last_ball_pos = None
initialized = False
def scene_update_handler(scene):
    global last_ball_pos, initialized
    if bpy.context.mode == 'OBJECT':
        try:
            ball = bpy.data.objects["Ball"]
            current_pos = ball.matrix_world.translation.copy()
            if not initialized:
                print("场景初始化，跳过首次更新")
                last_ball_pos = current_pos
                initialized = True
                return
            if last_ball_pos is None or (current_pos - last_ball_pos).length > 0.1:
                #print("处理程序触发")
                base = bpy.data.objects["BasePlate"]
                slider = bpy.data.objects["Slider"]
                end_hand = bpy.data.objects["EndHand"]
                move_to_target(base, slider, end_hand, ball)
                last_ball_pos = current_pos
        except KeyError as e:
            print(f"错误: 场景中未找到对象 {e}")

# 主程序
def main():
    clear_scene()
    base = create_base_plate()
    column = create_vertical_column(base)
    slider = create_slider(column)
    end_hand = create_end_hand(slider)
    ball = create_target_ball()
    
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(scene_update_handler)

# 运行主程序
main()
