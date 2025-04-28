from si_fab import all as pdk
import ipkiss3.all as i3
from ipkiss.technology import get_technology
import math
TECH = get_technology()

class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    core_width = i3.PositiveNumberProperty(default=0.5, doc="width of core.")

    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            w_tpl = pdk.RibWaveguideTemplate()
            w_tpl.Layout(core_width=self.core_width)
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0, trace_template=w_tpl)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0, trace_template=w_tpl)
            return ports


class customTaper(i3.PCell):
    _name_prefix = "customTaper"
    taperW1 = i3.PositiveNumberProperty(default=0.5, doc="taperW1.")
    taperW2 = i3.PositiveNumberProperty(default=3, doc="taperW2.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.RibWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            taperW1 = self.taperW1
            taperW2 = self.taperW2
            taperLength = self.taperLength
            core = self.trace_template.core_layer

            elems_to_merge_core = [i3.Wedge(
                layer=core,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1,
                end_width=taperW2,
            )]
            elems += i3.merge_elements(elems_to_merge_core, core)

            return elems

        def _generate_ports(self, ports):
            tt_1 = pdk.RibWaveguideTemplate()
            tt_1.Layout(core_width=self.taperW1)
            tt_2 = pdk.RibWaveguideTemplate()
            tt_2.Layout(core_width=self.taperW2)
            taperLength = self.taperLength
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0, trace_template=tt_1)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0, trace_template=tt_2)
            return ports


class custom_dichroic (i3.PCell):
    _name_prefix = "custom_dichroic"
    B_width = i3.PositiveNumberProperty(default=0.264, doc="Width of the B waveguide")
    B_length = i3.PositiveNumberProperty(default=1160., doc="B_length not change")
    B_taper_length = i3.PositiveNumberProperty(default=200., doc="Length of the B start change")
    B_taper_wider = i3.PositiveNumberProperty(default=0.14, doc="B1B3 width of the end ")
    gb = i3.PositiveNumberProperty(default=0.2, doc="b waveguide distance")

    ga = i3.PositiveNumberProperty(default=0.14, doc="a-b waveguide distance")
    A_taper_wider = i3.PositiveNumberProperty(default=0.14, doc="A width of the end ")
    A_width = i3.PositiveNumberProperty(default=0.302, doc="Width of the A waveguide")
    g = i3.PositiveNumberProperty(default=5, doc="a-b waveguide final distance")
    A_taper_length = i3.PositiveNumberProperty(default=260, doc="L1 A length of the end ")

    trace_template = i3.TraceTemplateProperty(
        default=pdk.RibWaveguideTemplate().Layout(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            B_length = self.B_length
            B_width = self.B_width
            B_taper_wider = self.B_taper_wider
            B2_taper_width=3*B_width-2*B_taper_wider
            B_taper_length = self.B_taper_length
            B2_in_length = 0
            gb = self.gb

            ga = self.ga
            A_taper_wider = self.A_taper_wider
            A_width = self.A_width
            g = self.g
            A_taper_length = self.A_taper_length

            core_layer = self.trace_template.core_layer
            # B2
            elems += i3.Rectangle(layer=core_layer,
                                  center=(0, 0),
                                  box_size=(B_length, B_width))
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(-B_length / 2, 0),
                end_coord=(-B_length / 2 - B_taper_length, 0.),
                begin_width=B_width,
                end_width=B2_taper_width,
            )
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(B_length / 2, 0),
                end_coord=(B_length / 2 + B_taper_length, 0.),
                begin_width=B_width,
                end_width=B2_taper_width,
            )
            #头尾收束到0.5
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(B_length / 2 + B_taper_length, 0),
                end_coord=(B_length / 2 + B_taper_length+3, 0.),
                begin_width=B2_taper_width,
                end_width=0.5,
            )
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(-B_length / 2 - B_taper_length, 0),
                end_coord=(-B_length / 2 - B_taper_length - 3, 0.),
                begin_width=B2_taper_width,
                end_width=0.5,
            )
            # B3
            elems += i3.Rectangle(layer=core_layer,
                                  center=(0, -B_width - gb),
                                  box_size=(B_length, B_width))
            elems += i3.Rectangle(layer=core_layer,
                                  center=(B_length / 2 + B_taper_length / 2, -3 * B_width / 2 - gb + B_taper_wider / 2),
                                  box_size=(B_taper_length, B_taper_wider))
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(B_length / 2, -3 * B_width / 2 - gb + B_taper_wider), (B_length / 2, -B_width / 2 - gb),
                       (B_length / 2 + B_taper_length, -3 * B_width / 2 - gb + B_taper_wider)
                       ])
            elems += i3.Rectangle(layer=core_layer,
                                  center=(
                                  -B_length / 2 - B_taper_length / 2, -3 * B_width / 2 - gb + B_taper_wider / 2),
                                  # box_size=(Width2, Length))
                                  box_size=(B_taper_length, B_taper_wider))
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(-B_length / 2, -3 * B_width / 2 - gb + B_taper_wider), (-B_length / 2, -B_width / 2 - gb),
                       (-B_length / 2 - B_taper_length, -3 * B_width / 2 - gb + B_taper_wider)
                       ])
            # B1
            elems += i3.Rectangle(layer=core_layer,
                                  center=(0, B_width + gb),
                                  # box_size=(Width2, Length))
                                  box_size=(B_length, B_width))
            elems += i3.Rectangle(layer=core_layer,
                                  center=(B_length / 2 + B_taper_length / 2, 3 * B_width / 2 + gb - B_taper_wider / 2),
                                  # box_size=(Width2, Length))
                                  box_size=(B_taper_length, B_taper_wider))
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(B_length / 2, 3 * B_width / 2 + gb - B_taper_wider), (B_length / 2, B_width / 2 + gb),
                       (B_length / 2 + B_taper_length, 3 * B_width / 2 + gb - B_taper_wider)
                       ])
            elems += i3.Rectangle(layer=core_layer,
                                  center=(-B_length / 2 - B_taper_length / 2, 3 * B_width / 2 + gb - B_taper_wider / 2),
                                  # box_size=(Width2, Length))
                                  box_size=(B_taper_length, B_taper_wider))
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(-B_length / 2, 3 * B_width / 2 + gb - B_taper_wider), (-B_length / 2, B_width / 2 + gb),
                       (-B_length / 2 - B_taper_length, 3 * B_width / 2 + gb - B_taper_wider)
                       ])

            # A
            elems += i3.Rectangle(layer=core_layer,
                                  center=(
                                  -B_length / 2 + A_taper_length / 2, -3 * B_width / 2 - gb - A_taper_wider / 2 - ga),
                                  # box_size=(Width2, Length))
                                  box_size=(A_taper_length, A_taper_wider))
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(-B_length / 2, -3 * B_width / 2 - gb - A_taper_wider - ga),
                       (-B_length / 2 + A_taper_length, -3 * B_width / 2 - gb - A_taper_wider - ga),
                       (-B_length / 2 + A_taper_length, -3 * B_width / 2 - gb - A_width - ga)
                       ])
            elems += i3.Boundary(
                layer=core_layer,
                shape=[(-B_length / 2 + A_taper_length, -3 * B_width / 2 - gb - ga),
                       (-B_length / 2 + A_taper_length, -3 * B_width / 2 - gb - A_width - ga),
                       (B_length / 2, -3 * B_width / 2 - gb - A_width - g),
                       (B_length / 2, -3 * B_width / 2 - gb - g)
                       ])
            elems += i3.Rectangle(layer=core_layer,
                                  center=(
                                      B_length / 2 + B_taper_length / 2 + B2_in_length / 2,
                                      -3 * B_width / 2 - gb - A_width / 2 - g),
                                  box_size=(B_taper_length + B2_in_length, A_width))
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(B_length / 2 + B_taper_length+ B2_in_length, -3 * B_width / 2 - gb - A_width / 2 - g),
                end_coord=(B_length / 2 + B_taper_length+ B2_in_length + 3, -3 * B_width / 2 - gb - A_width / 2 - g),
                begin_width=A_width,
                end_width=0.5,
            )
            return elems
        def _generate_ports(self, ports):
            B_length = self.B_length
            B_width = self.B_width
            B_taper_length = self.B_taper_length
            B_taper_wider = self.B_taper_wider
            B2_in_length = 0
            gb = self.gb
            B2_taper_width = 3 * B_width - 2 * B_taper_wider

            ga = self.ga
            A_taper_wider = self.A_taper_wider
            A_width = self.A_width
            g = self.g
            A_taper_length = self.A_taper_length

            w_tpl = pdk.RibWaveguideTemplate()
            w_tpl.Layout(core_width=0.5)

            w_bus = pdk.RibWaveguideTemplate()
            w_bus.Layout(core_width=0.5)

            ports += i3.OpticalPort(
                name="in",
                position=(-B_length / 2 - B_taper_length - B2_in_length-3, 0),
                angle=180.0,
                trace_template=w_tpl,
            )
            ports += i3.OpticalPort(
                name="out1",
                position=(B_length / 2 + B_taper_length + B2_in_length+3, 0),
                angle=0.0,
                trace_template=w_tpl,
            )
            ports += i3.OpticalPort(
                name="out2",
                position=(B_length / 2 + B_taper_length + B2_in_length+3, -3 * B_width / 2 - gb - A_width / 2 - g),
                angle=0.0,
                trace_template=w_bus,
            )
            return ports


class dichroicFoundryArmTest(i3.PCell):
    _name_prefix = "dichroic2x2"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.RibWaveguideTemplate().Layout(core_width=0.2),
        doc="Trace template of the access waveguide"
    )
#B
    B_width = i3.PositiveNumberProperty(default=0.264, doc="Width of the B waveguide")
    B_length = i3.PositiveNumberProperty(default=1160., doc="B_length not change")
    B_taper_length = i3.PositiveNumberProperty(default=200., doc="Length of the B start change")
    B_taper_wider = i3.PositiveNumberProperty(default=0.14, doc="B1B3 width of the end ")
    gb = i3.PositiveNumberProperty(default=0.2, doc="b waveguide distance")
#A
    ga = i3.PositiveNumberProperty(default=0.14, doc="a-b waveguide distance")
    A_taper_wider = i3.PositiveNumberProperty(default=0.14, doc="A width of the end ")
    A_width = i3.PositiveNumberProperty(default=0.302, doc="Width of the A waveguide")
    g = i3.PositiveNumberProperty(default=5, doc="a-b waveguide final distance")
    A_taper_length = i3.PositiveNumberProperty(default=260, doc="L1 A length of the end ")

    offset_lateral = i3.PositiveNumberProperty(default=15, doc="lateral offset of port.")
    offset_vertical = i3.PositiveNumberProperty(default=5, doc="vertical offset of port.")

    w_bus = i3.PositiveNumberProperty(default=0.5, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.5, doc="Width of the drop waveguide, act as output")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            B2_taper_width = 3 * self.B_width - 2 * self.B_taper_wider

            offset_lateral = self.offset_lateral
            offset_vertical = self.offset_vertical

            w_port = 0.5
            taper_length = 10
            wire_tpl_drop = pdk.RibWaveguideTemplate()
            wire_tpl_drop.Layout(core_width=self.w_drop)
            wire_tpl_bus = pdk.RibWaveguideTemplate()
            wire_tpl_bus.Layout(core_width=self.w_bus)


            insts_insts = {
                'dichroic': custom_dichroic(
                    gb=self.gb,
                    B_width=self.B_width,
                    B_length=self.B_length,
                    B_taper_length=self.B_taper_length,
                    B_taper_wider=self.B_taper_wider,
                    ga=self.ga,
                    A_taper_wider=self.A_taper_wider,
                    A_width=self.A_width,
                    g=self.g,
                    A_taper_length=self.A_taper_length,
                ),

                'TempPort_in': TempPort(core_width=self.w_bus),

                'TempPort_through': TempPort(core_width=self.w_drop),

                'TempPort_add': TempPort(core_width=self.w_bus),

                'taper_in': customTaper(taperW1=w_port,
                                        taperW2=self.w_bus,
                                        taperLength=taper_length),

                'taper_through': customTaper(taperW1=w_port,
                                             taperW2=self.w_drop,
                                             taperLength=taper_length),

                'taper_add': customTaper(taperW1=self.w_drop,
                                         taperW2=w_port,
                                         taperLength=taper_length),
            }
            insts_specs = [
                i3.PlaceRelative('TempPort_in:out', 'dichroic:in',
                                 (-15,0)),#-offset_lateral, offset_vertical
                i3.ConnectBend('TempPort_in:out', 'dichroic:in', trace_template=wire_tpl_bus),
                i3.PlaceRelative('taper_in:out', 'TempPort_in:out',
                                 (0, 0)),
                i3.PlaceRelative('TempPort_through:in', 'dichroic:out1',
                                 (offset_lateral, offset_vertical)),
                i3.ConnectBend('TempPort_through:in', 'dichroic:out1', bend_radius=10
                               , trace_template=wire_tpl_bus),
                i3.PlaceRelative('taper_through:in', 'TempPort_through:out',
                                 (0, 0)),
                i3.PlaceRelative('TempPort_add:in', 'dichroic:out2',
                                 (offset_lateral, -offset_vertical)),
                i3.ConnectBend('TempPort_add:in', 'dichroic:out2', bend_radius=10
                               , trace_template=wire_tpl_drop),
                i3.PlaceRelative('taper_add:in', 'TempPort_add:out',
                                 (0, 0)),
            ]
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts
        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'taper_in:in': 'in',
                                         'taper_through:out': 'out1',
                                         'taper_add:out': 'out2',
                                     })
            return ports

class dichroicrow(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            insts_insts = {}
            insts_specs = []

            gap_GACDC_GC = 120
            gap_GACDCS = 50
            for i in range(32):
                if i == 16:
                    pass
                else:
                    insts_insts[f'GC_{i + 1}'] = pdk.AMF_Si_GC1D_Cband()
                    insts_specs += [i3.Place(f'GC_{i + 1}:opt_1_si', (0, i * 130), angle=0)]
            B_widths = [0.259, 0.260, 0.261, 0.262, 0.263, 0.264, 0.265, 0.266, 0.267]
            for i in range(9):
                insts_insts[f'dichroic_{i + 1}'] = custom_dichroic(
                    B_width=B_widths[i],
                )
            # 4299.246600813283
            insts_specs += [i3.ConnectManhattan('GC_1:opt_1_si', 'GC_32:opt_1_si',
                                                control_points=[
                                                    i3.START + (-50, -50),
                                                    i3.START + (-70, 2000),
                                                    i3.END + (-50, 50)
                                                ]),
                            i3.ConnectManhattan('GC_30:opt_1_si', 'GC_31:opt_1_si',
                                                control_points=[
                                                    i3.START + (-50, -50),
                                                    i3.START + (-70, 100),
                                                    i3.END + (-50, 50)
                                                ])
                            ]
            insts_specs += [
                i3.PlaceRelative('dichroic_1', 'GC_8:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 1, 0), angle=-90),
                i3.PlaceRelative('dichroic_2', 'GC_8:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 2, 0), angle=-90),
                i3.PlaceRelative('dichroic_3', 'GC_8:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 3, 0), angle=-90),
                i3.PlaceRelative('dichroic_4', 'GC_8:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 4, 0), angle=-90),
                i3.PlaceRelative('dichroic_5', 'GC_8:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 5, 0), angle=-90),
                i3.PlaceRelative('dichroic_6', 'GC_25:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 1, 0), angle=-90),
                i3.PlaceRelative('dichroic_7', 'GC_25:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 2, 0), angle=-90),
                i3.PlaceRelative('dichroic_8', 'GC_25:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 3, 0), angle=-90),
                i3.PlaceRelative('dichroic_9', 'GC_25:opt_1_si',
                                 (gap_GACDC_GC + gap_GACDCS * 4, 0), angle=-90),

            ]
            insts_specs_group1_up = [

                i3.ConnectManhattan('dichroic_1:in', 'GC_12:opt_1_si',
                                    control_points=[
                                        i3.H(2150 -10 * 5), i3.V(gap_GACDC_GC - 10 * 1)
                                    ]),
                i3.ConnectManhattan('dichroic_2:in', 'GC_13:opt_1_si',
                                    control_points=[
                                        i3.H(2150 - 10 * 4), i3.V(gap_GACDC_GC - 10 * 5)
                                    ]),
                i3.ConnectManhattan('dichroic_3:in', 'GC_14:opt_1_si',
                                    control_points=[
                                        i3.H(2150 - 10 * 3), i3.V(gap_GACDC_GC - 10 * 7)
                                    ]),
                i3.ConnectManhattan('dichroic_4:in', 'GC_15:opt_1_si',
                                    control_points=[
                                        i3.H(2150 - 10 * 2), i3.V(gap_GACDC_GC - 10 * 9)
                                    ]),
                i3.ConnectManhattan('dichroic_5:in', 'GC_16:opt_1_si',
                                    control_points=[
                                        i3.H(2150 - 10 * 1), i3.V(gap_GACDC_GC - 10 * 10)
                                    ]),

            ]
            insts_specs_group1_down = [
                i3.ConnectManhattan('dichroic_1:out2', 'GC_11:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 9), i3.V(gap_GACDC_GC - 10 * 1)
                                    ]),
                i3.ConnectManhattan('dichroic_1:out1', 'GC_10:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 10), i3.V(gap_GACDC_GC - 10 * 2)
                                    ]),
                i3.ConnectManhattan('dichroic_2:out2', 'GC_9:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 11), i3.V(gap_GACDC_GC - 10 * 3)
                                    ]),
                i3.ConnectManhattan('dichroic_2:out1', 'GC_8:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 12), i3.V(gap_GACDC_GC - 10 * 4)
                                    ]),
                i3.ConnectManhattan('dichroic_3:out2', 'GC_7:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 13), i3.V(gap_GACDC_GC - 10 * 5)
                                    ]),
                i3.ConnectManhattan('dichroic_3:out1', 'GC_6:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 14), i3.V(gap_GACDC_GC - 10 * 6)
                                    ]),
                i3.ConnectManhattan('dichroic_4:out2', 'GC_5:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 15), i3.V(gap_GACDC_GC - 10 * 7)
                                    ]),
                i3.ConnectManhattan('dichroic_4:out1', 'GC_4:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 16), i3.V(gap_GACDC_GC - 10 * 8)
                                    ]),
                i3.ConnectManhattan('dichroic_5:out2', 'GC_3:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 17), i3.V(gap_GACDC_GC - 10 * 9)
                                    ]),
                i3.ConnectManhattan('dichroic_5:out1', 'GC_2:opt_1_si',
                                    control_points=[
                                        i3.H(200 - 10 * 18), i3.V(gap_GACDC_GC - 10 * 10)
                                    ]),
            ]
            insts_specs_group2_up = [

                i3.ConnectManhattan('dichroic_6:in', 'GC_26:opt_1_si',
                                    control_points=[
                                        i3.H(3850 + 10 * 7), i3.V(gap_GACDC_GC - 10 * 4)
                                    ]),
                i3.ConnectManhattan('dichroic_7:in', 'GC_27:opt_1_si',
                                    control_points=[
                                        i3.H(3850 + 10 * 10), i3.V(gap_GACDC_GC - 10 * 5)
                                    ]),
                i3.ConnectManhattan('dichroic_8:in', 'GC_28:opt_1_si',
                                    control_points=[
                                        i3.H(3850 + 10 * 11), i3.V(gap_GACDC_GC - 10 * 6)
                                    ]),
                i3.ConnectManhattan('dichroic_9:in', 'GC_29:opt_1_si',
                                    control_points=[
                                        i3.H(3850 + 10 * 12), i3.V(gap_GACDC_GC - 10 * 7)
                                    ]),
            ]
            insts_specs_group2_down = [
                i3.ConnectManhattan('dichroic_6:out2', 'GC_25:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 10), i3.V(gap_GACDC_GC + 10 * 2)
                                    ]),
                i3.ConnectManhattan('dichroic_6:out1', 'GC_24:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 9), i3.V(gap_GACDC_GC + 10 * 1)
                                    ]),
                i3.ConnectManhattan('dichroic_7:out2', 'GC_23:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 8), i3.V(gap_GACDC_GC - 10 * 0)
                                    ]),
                i3.ConnectManhattan('dichroic_7:out1', 'GC_22:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 7), i3.V(gap_GACDC_GC - 10 * 1)
                                    ]),
                i3.ConnectManhattan('dichroic_8:out2', 'GC_21:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 6), i3.V(gap_GACDC_GC - 10 * 2)
                                    ]),
                i3.ConnectManhattan('dichroic_8:out1', 'GC_20:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 5), i3.V(gap_GACDC_GC - 10 * 3)
                                    ]),
                i3.ConnectManhattan('dichroic_9:out2', 'GC_19:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 4), i3.V(gap_GACDC_GC - 10 * 4)
                                    ]),
                i3.ConnectManhattan('dichroic_9:out1', 'GC_18:opt_1_si',
                                    control_points=[
                                        i3.H(2150 + 10 * 3), i3.V(gap_GACDC_GC - 10 * 5)
                                    ]),
            ]
            insts_specs += insts_specs_group1_up
            insts_specs += insts_specs_group1_down
            insts_specs += insts_specs_group2_up
            insts_specs += insts_specs_group2_down

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts


if __name__ == '__main__':
    lo = dichroicrow()

    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('custom_dichroic.gds')
