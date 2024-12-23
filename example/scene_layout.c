    arm_2d_canvas(ptTile, my_canvas) {
        arm_2d_align_centre(my_canvas, 240, 128) {
        }
        arm_2d_align_top_left(my_canvas, 100, 50) {
        }
        arm_2d_align_bottom_right(my_canvas, 200, 100) {
            arm_2d_layout(__bottom_region) {
                __item_line_horizontal(60, 80) {
                }
                __item_line_dock_horizontal(100) {
                }
            }
        }
        arm_2d_dock_top(my_canvas, 100, 10) {
        }
        arm_2d_dock(my_canvas, 200, 100, 5) {
        }
        arm_2d_layout(__bottom_region) {
            __item_vertical(60, 80) {
            }
            __item_vertical(28, 100) {
            }
        }
    }