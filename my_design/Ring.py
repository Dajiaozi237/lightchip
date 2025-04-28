from si_fab import all as pdk
from ipkiss3 import all as i3
import numpy as np
from si_fab.technology import TECH

class Ring_FSR200G_26(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports


class Ring_FSR200G_28(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports


class Ring_FSR200G_30(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.30 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports



class Ring_FSR200G_32(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.32 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=10, layer=i3.TECH.PPLAYER.M1)
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )

            return ports



class Ring_FSR200G_34(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.34 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=10, layer=i3.TECH.PPLAYER.M1)
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )

            return ports



class Ring_FSR200G_36(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.36 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=10, layer=i3.TECH.PPLAYER.M1)
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )

            return ports



class Ring_FSR200G_38(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.38 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports



class Ring_FSR200G_40(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.40 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports



class Ring_FSR200G_42(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.42 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports



class Ring_FSR200G_44(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.44 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports


class Ring_FSR200G_46(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.46 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                )

            return ports


class Ring_FSR200G(i3.PCell):
    _name_prefix = "Ring_FSR200G"
    wg_template = i3.WaveguideTemplateProperty(default=pdk.SWG450(), doc="trace template used for the bus")
    bus_wg = i3.ChildCellProperty(doc="the bus waveguide")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")

    def _default_bus_wg(self):
        # waveguide cell
        bus_wg = i3.RoundedWaveguide(name=self.name + "_bus",
                                     trace_template=self.wg_template)

        return bus_wg

    class Layout(i3.LayoutView):
        radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
        spacing = i3.PositiveNumberProperty(default=0.35 + 0.45,
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

            radius = self.radius
            spacing = self.spacing - 0.45
            bus_angle = self.bus_angle
            labelText = f'Period:{radius:.1f}um  Spacing:{spacing * 1000:.1f}nm  Bus_angle:{bus_angle:.1f} degree'
            if self.textMarker:
                elems += i3.PolygonText(
                    layer=TECH.PPLAYER.DOC,
                    text=labelText,
                    alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                    coordinate=(-radius, radius + 10.),
                    font=0, height=3
                )

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
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_L_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )
                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.M1,
                    shape=m1_R_shape.modified_copy(closed=False),
                    line_width=self.m1_width
                )

            return elems

        def _generate_ports(self, ports):
            # the connection to the outside world
            # ports += self.instances["bus"].ports

            # print(f"{self.instances['bus'].ports['in'].x}, {self.instances['bus'].ports['in'].y}")
            # print(f"{self.instances['bus'].ports['out'].x}, {self.instances['bus'].ports['out'].y}")
            xin = self.instances['bus'].ports['in'].x
            yin = self.instances['bus'].ports['in'].y
            ports += i3.OpticalPort(
                name="in",
                position=(xin+0.1, yin),
                angle=180.,
            )
            xout = self.instances['bus'].ports['out'].x
            yout = self.instances['bus'].ports['out'].y
            ports += i3.OpticalPort(
                name="out",
                position=(xout - 0.1, yout),
                angle=0.,
            )
            # print(self.instances["bus"].port['in'].y)
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
                    position=i3.Coord2(ht_shapeL[0].x, ht_shapeL[0].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )
                ports += i3.ElectricalPort(
                    name="elec2",
                    position=i3.Coord2(ht_shapeR[-1].x, ht_shapeR[-1].y - self.m1_length),
                    angle=270.,
                    trace_template=tt,
                )

            return ports
if __name__ == '__main__':
    lo = Ring_FSR200G_26()
    lo.Layout().visualize(annotate=True)

    lo.Layout().write_gdsii('Ring_FSR200G_26.gds')

