from si_fab import all as pdk
import ipkiss3.all as i3
import numpy as np
from ipkiss.technology import get_technology
from cell_DC9010 import Direction_coupler_90_10


TECH = get_technology()


class TextPCell(i3.PCell):
    # _name_prefix = "Text"
    text = i3.StringProperty(doc='display', default=' ')

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            labelText = self.text
            elems = i3.PolygonText(
                layer=i3.TECH.PPLAYER.MT2,
                # layer=TECH.PPLAYER.NONE,
                text=labelText,
                alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                coordinate=(0, 0.),
                font=0, height=30
            )
            return elems

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name='LOC', position=(0, 0.), angle=0)
            return ports


class Ring_doubleBus(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=28, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.22 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_150(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=28, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.15 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                via2width = 8
                elems += i3.Rectangle(
                    layer=TECH.PPLAYER.M1,
                    center=(ht_shapeL[0].x, ht_shapeL[0].y - via2width / 2),
                    box_size=(via2width, via2width)
                )
                elems += i3.Rectangle(
                    layer=TECH.PPLAYER.M1,
                    center=(ht_shapeL[0].x, ht_shapeL[0].y - via2width / 2),
                    box_size=(self.m1_width, self.m1_width)
                )

                elems += i3.Rectangle(
                    layer=TECH.PPLAYER.M1,
                    center=(ht_shapeR[-1].x, ht_shapeR[-1].y - via2width / 2),
                    box_size=(via2width, via2width)
                )
                elems += i3.Rectangle(
                    layer=TECH.PPLAYER.M1,
                    center=(ht_shapeR[-1].x, ht_shapeR[-1].y - via2width / 2),
                    box_size=(self.m1_width, self.m1_width)
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_160(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=28, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.16 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_170(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.17 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_180(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.18 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_190(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.19 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_200(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.20 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_210(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.21 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_220(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.22 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_230(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.23 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_240(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.24 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_250(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.25 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_260(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.26 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_270(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.27 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class Ring_doubleBus_280(i3.PCell):
    _name_prefix = "Ring_doubleBus"
    wg_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.28 + 0.45,
                                            doc="spacing between centerline of bus waveguide and edge of the disk")
        bus_angle = i3.PositiveNumberProperty(default=30.0,
                                              doc="angular span (in degrees) of the bus waveguide around the disk")
        m1_width = i3.PositiveNumberProperty(default=10.0, doc='heater contact width')
        m1_length = i3.PositiveNumberProperty(default=5.0, doc='heater contact m1_length')
        heater_angle = i3.PositiveNumberProperty(default=270., doc='heater contact m1_length')

        def _default_bus_wg(self):
            # set the layout parameters of the waveguide
            r = self.radius + self.spacing
            a = 0.5 * self.bus_angle
            s = i3.TECH.WG.SHORT_STRAIGHT

            # Bus waveguide layout
            bus_layout = self.cell.bus_wg.get_default_view(i3.LayoutView)  # default bus layout view
            bus_layout.set(bend_radius=r,
                           trace_template=self.wg_template)

            b1, b2 = bus_layout.get_bend_size(a)  # calculates the size of the waveguide bend

            # control shape for the bus waveguide (one half)
            # the RoundedWaveguide will automatically generate smooth bends
            s1 = i3.Shape([(-b1, -r)])
            s1.add_polar(2 * b2, 180.0 - a)
            s1.add_polar(b1 + s, 180.0)

            # stitching 2 halves together
            bus_shape = s1.reversed() + s1.h_mirror_copy()

            # assigning the shape to the bus
            bus_layout.set(shape=bus_shape,
                           draw_control_shape=False)
            return bus_layout

        def _generate_instances(self, insts):
            insts += i3.SRef(name="bus",
                             reference=self.bus_wg)  # Adding an instance of the bus as a hierarchical component
            insts += i3.SRef(name="bustop",
                             reference=self.bus_wg,
                             transformation=i3.Rotation(rotation_center=(0.0, 0.0), rotation=180.0)
                             )
            return insts

        def _generate_elements(self, elems):
            # define the disk as pure geometric elements
            # TECH.PPLAYER.NONE
            wg_width = self.wg_template.core_width
            outer_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius + wg_width / 2,
                                   angle_step=1.0
                                   )
            inner_ring = i3.Circle(layer=TECH.PPLAYER.SI,
                                   radius=self.radius - wg_width / 2,
                                   angle_step=1.0
                                   )
            none_outer_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius + 3.5 + wg_width / 2,
                                        angle_step=1.0
                                        )
            none_inner_ring = i3.Circle(layer=TECH.PPLAYER.NONE,
                                        radius=self.radius - 3.5 - wg_width / 2,
                                        angle_step=1.0
                                        )
            elems += i3.subtract_elements([outer_ring], [inner_ring])
            elems += i3.subtract_elements([none_outer_ring], [none_inner_ring])

            #elems += i3.subtract_elements([outer_ring], [inner_ring])

            if self.heater_open:
                heater_hw = 3.

                # Draw heater
                # Use windows which we extrude along the generic waveguide shape
                heater_windows = [
                    i3.PathTraceWindow(
                        start_offset=-0.5 * heater_hw,
                        end_offset=0.5 * heater_hw,
                        layer=i3.TECH.PPLAYER.HT
                    )
                ]

                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                # ht_shape = ht_shapeL + ht_shapeC + ht_shapeR
                ht_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) \
                           + ht_shapeL + ht_shapeC + ht_shapeR \
                           + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))
                center_line = ht_shapeL + ht_shapeC + ht_shapeR
                for h in heater_windows:
                    elems += h.get_elements_from_shape(shape=center_line)

                m1_L_shape = i3.Shape(i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length)) + ht_shapeL
                m1_R_shape = ht_shapeR + i3.Shape(i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length))

                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            # the connection to the outside world
            # ports += self.instances["bus"].ports
            t = self.instances["bus"].ports[0]
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.OpticalPort(
                name="in",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bus"].ports[1]
            ports += i3.OpticalPort(
                name="through",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            t = self.instances["bustop"].ports[0]
            ports += i3.OpticalPort(
                name="add",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
                                    )

            t = self.instances["bustop"].ports[1]
            ports += i3.OpticalPort(
                name="drop",
                position=i3.Coord2(t.x, t.y),
                angle=t.angle,
            )

            if self.heater_open:
                a = (360 - self.heater_angle) / 2
                b = 90 - a
                smallRx = (self.radius + self.m1_length) * np.sin(np.deg2rad(a))
                smallRy = (self.radius + self.m1_length) * np.cos(np.deg2rad(a))
                ht_shapeC = i3.ShapeArc(radius=self.radius, start_angle=-90 - a, end_angle=-90 - a - self.heater_angle,
                                        clockwise=True)
                ht_shapeL = i3.ShapeArc(center=(-smallRx, -smallRy), radius=self.m1_length, start_angle=0, end_angle=b)
                ht_shapeR = i3.ShapeArc(center=(smallRx, -smallRy), radius=self.m1_length, start_angle=-180 - b,
                                        end_angle=-180)
                ports += i3.ElectricalPort(
                    name="elec1",
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length + 0.005),
                    angle=270.,

                    trace_template=tt,
                )

            return ports

class TempPort(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=0.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=180.0)
            return ports

if __name__ == '__main__':
    lo = Ring_doubleBus()
    lo.Layout().visualize(annotate=True)

    lo.Layout().write_gdsii('RingDC.gds')

    a = lo.Layout().instances
    insts_dic = a
    c = 0
    for instance in insts_dic:
        if "_to_" in instance:
            print("This is the connector's instance. Print the length below.")
            print("{} length is {}:".format(instance, insts_dic[instance].reference.trace_length()))
            c = c + insts_dic[instance].reference.trace_length()
