from si_fab import all as pdk
from ipkiss3 import all as i3
# Importing the technology and IPKISS
from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.components.waveguides.wire import SiWireWaveguideTemplate
from si_fab.components.mmi.pcell.cell import WaveguideSBend
import math
import numpy as np
import sys  # 导入sys模块

sys.setrecursionlimit(3000)  # 将默认的递归深度修改为3000


def gaussian_apodization(current_period, total_period, a=1):
    apodization_factor = math.exp(-a * ((current_period - 0.5 * total_period) ** 2) / (total_period ** 2))
    return apodization_factor


def mis_alignment(current_period, total_period, apodization_function, apodization_strength=1):
    if apodization_function == 'Gaussian':
        mis_alignment_factor = gaussian_apodization(current_period, total_period, apodization_strength)
    return mis_alignment_factor


def lambda_to_period(lambda_resonance):
    """
    calculate grating period from desired resonance lambda
    """
    period = (lambda_resonance-0.6879) / 2.638
    return round(period, 4)


class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports




tt3 = pdk.SiWireWaveguideTemplate()
tt3.Layout(core_width=0.64,
              cladding_width=0.64 + 7)

tt4 = pdk.SiWireWaveguideTemplate()
tt4.Layout(core_width=0.41,
              cladding_width=0.41 + 7)

class Taper_TempPort1(i3.PCell):
    """
       in       ---------------------------------    out
    """
    _name_prefix = "Taper_in"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    width = i3.PositiveNumberProperty(default=0.45, doc="Width of the bus waveguide, act as input.")
    # tt3 = pdk.SiWireWaveguideTemplate()
    # tt3.Layout(core_width=0.64,
    #            cladding_width=0.64 + 7)

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):

            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer

            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, 0),
                end_coord=(15.0, 0),
                begin_width=self.width,
                end_width=0.45,
            )
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, 0),
                end_coord=(15.0, 0),
                begin_width=self.width + 7,
                end_width=0.45 + 7,
            )
            return elems


        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0, trace_template=tt3)
            ports += i3.OpticalPort(name="out", position=(15, 0.0), angle=0.0)
            return ports


class Taper_TempPort2(i3.PCell):
    """
       in       ---------------------------------    out
    """
    _name_prefix = "Taper_drop"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    width = i3.PositiveNumberProperty(default=0.45, doc="Width of the bus waveguide, act as input.")
    # tt3 = pdk.SiWireWaveguideTemplate()
    # tt3.Layout(core_width=0.64,
    #            cladding_width=0.64 + 7)

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):

            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer

            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, 0),
                end_coord=(15.0, 0),
                begin_width=self.width,
                end_width=0.45,
            )
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, 0),
                end_coord=(15.0, 0),
                begin_width=self.width + 7,
                end_width=0.45 + 7,
            )
            return elems


        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0, trace_template=tt4)
            ports += i3.OpticalPort(name="out", position=(15, 0.0), angle=0.0)
            return ports

class TempPort2(i3.PCell):
    """
       in       ---------------------------------    out
    """
    _name_prefix = "Temp_port"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    width = i3.PositiveNumberProperty(default=0.45, doc="Width of the bus waveguide, act as input.")
    # tt3 = pdk.SiWireWaveguideTemplate()
    # tt3.Layout(core_width=0.64,
    #            cladding_width=0.64 + 7)

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):

            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer

            elems += i3.Rectangle(
                layer=core_layer,
                center=(5, 0),
                box_size=(10, 0.45),
            )
            elems += i3.Rectangle(
                layer=cladding_layer,
                center=(5, 0),
                box_size=(10, 0.45 + 7),
            )
            return elems


        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(10, 0.0), angle=0.0)
            return ports

class custom_elec_single(i3.PCell):
    _name_prefix = "custom_elec"
    heater_width = i3.PositiveNumberProperty(default=3.8, doc="Width of the heater")
    heater_length = i3.PositiveNumberProperty(default=900., doc="heater_length")
    m1_taper_width = i3.PositiveNumberProperty(default=50., doc="Width of the M1 contact")
    m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
    m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            m1_taper_wider = self.m1_taper_wider
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1

            elems += i3.Rectangle(layer=Lh,
                                  center=(0, 0),
                                  # box_size=(Width2, Length))
                                  box_size=(heater_length, heater_width))
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(-heater_length / 2 + overlap_heater_m1, 0),
                end_coord=(-heater_length / 2 - m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(heater_length / 2 - overlap_heater_m1, 0),
                end_coord=(heater_length / 2 + m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1
            ports += i3.ElectricalPort(name='elec1',
                                       position=(heater_length / 2 + m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=0,
                                       trace_template=tt,
                                       )
            ports += i3.ElectricalPort(name='elec2',
                                       position=(-heater_length / 2 - m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=180,
                                       trace_template=tt,
                                       )
            ports += i3.OpticalPort(name='left_loc_of_heater', position=(-heater_length / 2, 0), )
            return ports


# class GACDCPhaseShiftApodized(i3.PCell):
#     """
#     bandpass filter based on grating assisted contra-directional coupler (GACDC)
#     apply phase-shift apodization
#
#     ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
#     →   add        ---------------------------------    drop  →（滤波输出端口）
#     ←   through    ---------------------------------    in    ←（输入端口）
#
#     中心波长和"grating_period"的关系：利用“lambda_to_period”函数算出
#
#     默认gap350nm，长度约800μm，带宽约1nm
#     """
#     # _name_prefix = "GACDCPhaseShiftApodized"
#     trace_template = i3.TraceTemplateProperty(
#         default=pdk.SiWireWaveguideTemplate(),
#         doc="Trace template of the access waveguide"
#     )
#     w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
#     w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
#     gap = i3.PositiveNumberProperty(default=0.40, doc="The gap between two waveguides.")
#     add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
#                                                                          "bus waveguide.")
#     grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
#                                                                               "on the bus waveguide.")
#     add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
#                                                                           "the drop waveguide.")
#     grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
#                                                                                "on the drop waveguide.")
#     lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
#     grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
#     num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
#     num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
#     apodization_function = i3.StringProperty(default='Gaussian',
#                                              doc="Apodization function: Gaussian")
#     apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")
#     class Layout(i3.LayoutView):
#
#         def _generate_elements(self, elems):
#             grating_width_bus_waveguide = self.grating_width_bus_waveguide
#             grating_width_drop_waveguide = self.grating_width_drop_waveguide
#             w_bus = self.w_bus
#             w_bus_port = w_bus + grating_width_bus_waveguide
#             w_drop = self.w_drop
#             w_drop_port = w_drop + grating_width_drop_waveguide
#             gap = self.gap
#             grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
#             # grating_period = self.grating_period
#             num_period = self.num_period
#             core_layer = self.trace_template.core_layer
#             cladding_layer = self.trace_template.cladding_layer
#             core_width = self.trace_template.core_width
#             num_side = self.num_side
#             coupling_length = grating_period * num_period
#             apodization_function = self.apodization_function
#             apodization_strength = self.apodization_strength
#
#             """
#             Si core
#             """
#             # 'add' port
#             elems += i3.Wedge(
#                 layer=core_layer,
#                 begin_coord=(0.0, gap / 2 + w_drop / 2),
#                 end_coord=(15.0, gap / 2 + w_drop / 2),
#                 begin_width=core_width,
#                 end_width=w_drop_port,
#             )
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(17.5, gap / 2 + w_drop / 2),
#                 box_size=(5, w_drop_port),
#             )
#             # 'through' port
#             elems += i3.Wedge(
#                 layer=core_layer,
#                 begin_coord=(0.0, -gap / 2 - w_bus / 2),
#                 end_coord=(15.0, -gap / 2 - w_bus / 2),
#                 begin_width=core_width,
#                 end_width=w_bus_port,
#             )
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(17.5, -gap / 2 - w_bus / 2),
#                 box_size=(5, w_bus_port),
#             )
#             # the drop waveguide
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(20 + coupling_length / 2, gap / 2 + w_drop / 2),
#                 box_size=(coupling_length, w_drop),
#             )
#             # the bus waveguide
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(20 + coupling_length / 2, -gap / 2 - w_bus / 2),
#                 box_size=(coupling_length, w_bus),
#             )
#             # add additional part, length=5
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(20 + coupling_length + 2.5, gap / 2 + w_drop / 2),
#                 box_size=(5, w_drop_port),
#             )
#
#             elems += i3.Rectangle(
#                 layer=core_layer,
#                 center=(20 + coupling_length + 2.5, -gap / 2 - w_bus / 2),
#                 box_size=(5, w_bus_port),
#             )
#             # 'drop' port
#             elems += i3.Wedge(
#                 layer=core_layer,
#                 begin_coord=(25 + coupling_length, gap / 2 + w_drop / 2),
#                 end_coord=(40 + coupling_length, gap / 2 + w_drop / 2),
#                 begin_width=w_drop_port,
#                 end_width=core_width,
#             )
#             # 'In' port
#             elems += i3.Wedge(
#                 layer=core_layer,
#                 begin_coord=(25 + coupling_length, -gap / 2 - w_bus / 2),
#                 end_coord=(40 + coupling_length, -gap / 2 - w_bus / 2),
#                 begin_width=w_bus_port,
#                 end_width=core_width,
#             )
#             # add gratings
#             # upside of the bus waveguide, apply misalignment
#             for i in range(int(num_period)):
#                 elems += i3.Rectangle(
#                     layer=core_layer,
#                     center=(20 + (0.25 + i) * grating_period +
#                             grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
#                                                                     apodization_strength)),
#                             -gap / 2 + grating_width_bus_waveguide / 2),
#                     box_size=(grating_period/2, grating_width_bus_waveguide),
#                 )
#             # down of the bus waveguide, apply misalignment
#             for i in range(int(num_period)):
#                 elems += i3.Rectangle(
#                     layer=core_layer,
#                     center=(20 + (0.25 + i) * grating_period +
#                             grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
#                                                                     apodization_strength)),
#                             -gap / 2 - w_bus - grating_width_bus_waveguide / 2),
#                     box_size=(grating_period/2, grating_width_bus_waveguide),
#                 )
#             # upside of the drop waveguide
#             for i in range(int(num_period)):
#                 elems += i3.Rectangle(
#                     layer=core_layer,
#                     center=(20 + (0.25 + i) * grating_period,
#                             gap / 2 - grating_width_drop_waveguide / 2),
#                     box_size=(grating_period/2, grating_width_drop_waveguide),
#                 )
#             # down of the input waveguide
#             for i in range(int(num_period)):
#                 elems += i3.Rectangle(
#                     layer=core_layer,
#                     center=(20 + (0.25 + i) * grating_period,
#                             gap / 2 + w_drop + grating_width_drop_waveguide / 2),
#                     box_size=(grating_period/2, grating_width_drop_waveguide),
#                 )
#             # Cladding
#             elems += i3.Wedge(
#                 layer=cladding_layer,
#                 begin_coord=(0.0, (w_drop - w_bus)/4),
#                 end_coord=(40 + coupling_length, (w_drop - w_bus)/4),
#                 begin_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
#                 end_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
#             )
#             return elems
#
#
#         def _generate_instance(self, elems):
#
#             Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
#             insts_insts = {
#                 'Sbend_in': Sbend,
#                 'Sbend_drop': Sbend,
#                 'Sbend_add': Sbend,
#                 'Sbend_through': Sbend,
#             }
#             insts_specs = [
#                 i3.FlipV('Sbend_in'),
#                 i3.FlipV('Sbend_add'),
#                 i3.Place('Sbend_in:out', (0, -gap / 2 - w_bus / 2)),
#                 i3.PlaceRelative('Sbend_drop:out', (0, gap / 2 + w_drop / 2)),
#                 i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
#                 i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),
#             ]
#             return insts
#
#         def _generate_ports(self, ports):
#             w_bus = self.w_bus
#             w_drop = self.w_drop
#             gap = self.gap
#             grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
#             num_period = self.num_period
#             coupling_length = grating_period * num_period
#             trace_template = self.trace_template
#
#             ports += i3.OpticalPort(
#                 name="add",
#                 position=(0.0, gap / 2 + w_drop / 2),
#                 angle=180.0,
#                 trace_template=trace_template,
#             )
#             ports += i3.OpticalPort(
#                 name="drop",
#                 position=(40 + coupling_length, gap / 2 + w_drop / 2),
#                 angle=0.0,
#                 trace_template=trace_template,
#             )
#             ports += i3.OpticalPort(
#                 name="in",
#                 position=(40 + coupling_length, -gap / 2 - w_bus / 2),
#                 angle=0.0,
#                 trace_template=trace_template,
#             )
#             ports += i3.OpticalPort(
#                 name="through",
#                 position=(0, -gap / 2 - w_bus / 2),
#                 angle=180.0,
#                 trace_template=trace_template,
#             )
#             return ports


class GACDCPhaseShiftApodized(i3.PCell):
    """
    bandpass filter based on grating assisted contra-directional coupler (GACDC)
    apply phase-shift apodization

    ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
    →   add        ---------------------------------    drop  →（滤波输出端口）
    ←   through    ---------------------------------    in    ←（输入端口）

    中心波长和"grating_period"的关系：利用“lambda_to_period”函数算出

    默认gap350nm，长度约800μm，带宽约1nm
    """
    # _name_prefix = "GACDCPhaseShiftApodized"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
    gap = i3.PositiveNumberProperty(default=0.40, doc="The gap between two waveguides.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
                                                                              "on the bus waveguide.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
                                                                               "on the drop waveguide.")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            w_bus = self.w_bus
            w_bus_port = w_bus + grating_width_bus_waveguide
            w_drop = self.w_drop
            w_drop_port = w_drop + grating_width_drop_waveguide
            gap = self.gap
            grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
            # grating_period = self.grating_period
            num_period = self.num_period
            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer
            core_width = self.trace_template.core_width
            num_side = self.num_side
            coupling_length = grating_period * num_period
            apodization_function = self.apodization_function
            apodization_strength = self.apodization_strength

            """
            Si core
            """
            # 'add' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(0.0, gap / 2 + w_drop / 2),
            #     end_coord=(15.0, gap / 2 + w_drop / 2),
            #     begin_width=core_width,
            #     end_width=w_drop_port,
            # )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, gap / 2 + w_drop / 2),
                box_size=(5, w_drop_port),
            )
            # 'through' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(0.0, -gap / 2 - w_bus / 2),
            #     end_coord=(15.0, -gap / 2 - w_bus / 2),
            #     begin_width=core_width,
            #     end_width=w_bus_port,
            # )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, -gap / 2 - w_bus / 2),
                box_size=(5, w_bus_port),
            )
            # the drop waveguide
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length / 2, gap / 2 + w_drop / 2),
                box_size=(coupling_length, w_drop),
            )
            # the bus waveguide
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length / 2, -gap / 2 - w_bus / 2),
                box_size=(coupling_length, w_bus),
            )
            # add additional part, length=5
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length + 2.5, gap / 2 + w_drop / 2),
                box_size=(5, w_drop_port),
            )

            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length + 2.5, -gap / 2 - w_bus / 2),
                box_size=(5, w_bus_port),
            )
            # 'drop' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(25 + coupling_length, gap / 2 + w_drop / 2),
            #     end_coord=(40 + coupling_length, gap / 2 + w_drop / 2),
            #     begin_width=w_drop_port,
            #     end_width=core_width,
            # )
            # 'In' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(25 + coupling_length, -gap / 2 - w_bus / 2),
            #     end_coord=(40 + coupling_length, -gap / 2 - w_bus / 2),
            #     begin_width=w_bus_port,
            #     end_width=core_width,
            # )
            # add gratings
            # upside of the bus waveguide, apply misalignment
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period +
                            grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                    apodization_strength)),
                            -gap / 2 + grating_width_bus_waveguide / 2),
                    box_size=(grating_period/2, grating_width_bus_waveguide),
                )
            # down of the bus waveguide, apply misalignment
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period +
                            grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                    apodization_strength)),
                            -gap / 2 - w_bus - grating_width_bus_waveguide / 2),
                    box_size=(grating_period/2, grating_width_bus_waveguide),
                )
            # upside of the drop waveguide
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period,
                            gap / 2 - grating_width_drop_waveguide / 2),
                    box_size=(grating_period/2, grating_width_drop_waveguide),
                )
            # down of the input waveguide
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period,
                            gap / 2 + w_drop + grating_width_drop_waveguide / 2),
                    box_size=(grating_period/2, grating_width_drop_waveguide),
                )
            # Cladding
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(15, (w_drop - w_bus)/4),
                end_coord=(40 + coupling_length - 15, (w_drop - w_bus)/4),
                begin_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
                end_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
            )
            return elems


        def _generate_instance(self, elems):

            Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {
                'Sbend_in': Sbend,
                'Sbend_drop': Sbend,
                'Sbend_add': Sbend,
                'Sbend_through': Sbend,
            }
            insts_specs = [
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.Place('Sbend_in:out', (0, -gap / 2 - w_bus / 2)),
                i3.PlaceRelative('Sbend_drop:out', (0, gap / 2 + w_drop / 2)),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),
            ]
            return insts

        def _generate_ports(self, ports):
            w_bus = self.w_bus
            w_drop = self.w_drop
            gap = self.gap
            grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
            num_period = self.num_period
            coupling_length = grating_period * num_period
            trace_template = self.trace_template

            ports += i3.OpticalPort(
                name="add",
                position=(15, gap / 2 + w_drop / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="drop",
                position=(40 + coupling_length - 15, gap / 2 + w_drop / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="in",
                position=(40 + coupling_length - 15, -gap / 2 - w_bus / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="through",
                position=(15, -gap / 2 - w_bus / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            return ports

class GACDCPhaseShiftApodizedWithArm(i3.PCell):
    """
    bandpass filter based on grating assisted contra-directional coupler (GACDC)
    apply phase-shift apodization

    ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
    →   add        ---------------------------------    drop  →（滤波输出端口）
    ←   through    ---------------------------------    in    ←（输入端口）

    中心波长和"grating_period"的关系：利用“lambda_to_period”函数算出

    默认gap350nm，长度约800μm，带宽约1nm
    """
    _name_prefix = "GACDCPhaseShiftApodizedWithArm"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
    gap = i3.PositiveNumberProperty(default=0.40, doc="The gap between two waveguides.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
                                                                              "on the bus waveguide.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
                                                                               "on the drop waveguide.")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")
    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            w_bus = self.w_bus
            w_bus_port = w_bus + grating_width_bus_waveguide
            w_drop = self.w_drop
            w_drop_port = w_drop + grating_width_drop_waveguide
            gap = self.gap
            grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
            # grating_period = self.grating_period
            num_period = self.num_period
            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer
            core_width = self.trace_template.core_width
            num_side = self.num_side
            coupling_length = grating_period * num_period
            apodization_function = self.apodization_function
            apodization_strength = self.apodization_strength

            """
            Si core
            """
            # 'add' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, gap / 2 + w_drop / 2),
                end_coord=(15.0, gap / 2 + w_drop / 2),
                begin_width=core_width,
                end_width=w_drop_port,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, gap / 2 + w_drop / 2),
                box_size=(5, w_drop_port),
            )
            # 'through' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, -gap / 2 - w_bus / 2),
                end_coord=(15.0, -gap / 2 - w_bus / 2),
                begin_width=core_width,
                end_width=w_bus_port,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, -gap / 2 - w_bus / 2),
                box_size=(5, w_bus_port),
            )
            # the drop waveguide
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length / 2, gap / 2 + w_drop / 2),
                box_size=(coupling_length, w_drop),
            )
            # the bus waveguide
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length / 2, -gap / 2 - w_bus / 2),
                box_size=(coupling_length, w_bus),
            )
            # add additional part, length=5
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length + 2.5, gap / 2 + w_drop / 2),
                box_size=(5, w_drop_port),
            )

            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + coupling_length + 2.5, -gap / 2 - w_bus / 2),
                box_size=(5, w_bus_port),
            )
            # 'drop' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + coupling_length, gap / 2 + w_drop / 2),
                end_coord=(40 + coupling_length, gap / 2 + w_drop / 2),
                begin_width=w_drop_port,
                end_width=core_width,
            )
            # 'In' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + coupling_length, -gap / 2 - w_bus / 2),
                end_coord=(40 + coupling_length, -gap / 2 - w_bus / 2),
                begin_width=w_bus_port,
                end_width=core_width,
            )
            # add gratings
            # upside of the bus waveguide, apply misalignment
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period +
                            grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                    apodization_strength)),
                            -gap / 2 + grating_width_bus_waveguide / 2),
                    box_size=(grating_period/2, grating_width_bus_waveguide),
                )
            # down of the bus waveguide, apply misalignment
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period +
                            grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                    apodization_strength)),
                            -gap / 2 - w_bus - grating_width_bus_waveguide / 2),
                    box_size=(grating_period/2, grating_width_bus_waveguide),
                )
            # upside of the drop waveguide
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period,
                            gap / 2 - grating_width_drop_waveguide / 2),
                    box_size=(grating_period/2, grating_width_drop_waveguide),
                )
            # down of the input waveguide
            for i in range(int(num_period)):
                elems += i3.Rectangle(
                    layer=core_layer,
                    center=(20 + (0.25 + i) * grating_period,
                            gap / 2 + w_drop + grating_width_drop_waveguide / 2),
                    box_size=(grating_period/2, grating_width_drop_waveguide),
                )
            # Cladding
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, (w_drop - w_bus)/4),
                end_coord=(40 + coupling_length, (w_drop - w_bus)/4),
                begin_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
                end_width=core_width + gap + (w_drop + w_bus)/2 + 7.0,
            )
            return elems


        def _generate_instance(self, elems):

            Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {
                'Sbend_in': Sbend,
                'Sbend_drop': Sbend,
                'Sbend_add': Sbend,
                'Sbend_through': Sbend,
            }
            insts_specs = [
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.Place('Sbend_in:out', (40 + coupling_length, -gap / 2 - w_bus / 2), angle=180),
                i3.PlaceRelative('Sbend_drop:out', (40 + coupling_length, gap / 2 + w_drop / 2), angle=180),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),
            ]
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            w_bus = self.w_bus
            w_drop = self.w_drop
            gap = self.gap
            grating_period = lambda_to_period(lambda_resonance=self.lambda_resonance)
            num_period = self.num_period
            coupling_length = grating_period * num_period
            trace_template = self.trace_template

            ports += i3.OpticalPort(
                name="add",
                position=(0.0, gap / 2 + w_drop / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="drop",
                position=(40 + coupling_length, gap / 2 + w_drop / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="in",
                position=(40 + coupling_length, -gap / 2 - w_bus / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="through",
                position=(0, -gap / 2 - w_bus / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            return ports


class GACDCWithArm(i3.PCell):
    """
        bandpass filter based on grating assisted contra-directional coupler (GACDC)
        apply phase-shift apodization

        ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
        →   add        ---------------------------------    drop  →（滤波输出端口）
        ←   through    ---------------------------------    in    ←（输入端口）

        中心波长和"grating_period"的关系：利用“lambda_to_period”函数算出

        默认gap350nm，长度约800μm，带宽约1nm
        """
    _name_prefix = "GACDCWithArm"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
    gap = i3.PositiveNumberProperty(default=0.35, doc="The gap between two waveguides.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
                                                                              "on the bus waveguide.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
                                                                               "on the drop waveguide.")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {
                'GACDC': GACDCPhaseShiftApodized(grating_period=self.grating_period,
                                                 num_period=self.num_period,
                                                 grating_width_bus_waveguide=self.grating_width_bus_waveguide,
                                                 grating_width_drop_waveguide=self.grating_width_drop_waveguide,
                                                 num_side=self.num_side,
                                                 w_bus=self.w_bus,
                                                 w_drop=self.w_drop,
                                                 gap=self.gap),
                # 'TempPort_in': TempPort(),
                # 'TempPort_drop': TempPort(),
                # 'TempPort_through': TempPort(),
                # 'TempPort_add': TempPort(),
                # 'TempPort_in': TempPort(),
                'Sbend_in': Sbend,
                'Sbend_drop': Sbend,
                'Sbend_add': Sbend,
                'Sbend_through': Sbend,
                # 'inarm': bend_in_out,
                # 'outarm': bend_in_out,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                i3.FlipH('GACDC'),
                i3.FlipV('GACDC'),
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.PlaceRelative('Sbend_in:out', 'GACDC:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'GACDC:drop', (0, 0)),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),
            ]
            # if self.heater_open:
            #     insts_insts['heater'] = custom_elec_single(m1_taper_width=10, )
            #     insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'GACDC:in', (19, -0.38)))

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Sbend_in:in': 'in',
                                         'Sbend_through:out': 'through',
                                         'Sbend_drop:in': 'drop',
                                         'Sbend_add:out': 'add',
                                         # # 'heater:elec1': 'elec2',
                                         # # 'heater:elec2': 'elec1',
                                     })
            # if self.heater_open:
            #     ports += i3.expose_ports(self.instances,
            #                              {
            #                                  'heater:elec1': 'elec2',
            #                                  'heater:elec2': 'elec1',
            #                              })
            return ports



# class GACDC_HT(i3.PCell):
#     """
#     ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
#     端口与“GACDCPhaseShiftApodized”的端口设置有区别，因为旋转了180度
#     →   in      ---------------------------------    through  →
#     ←   drop    ---------------------------------    add    ←
#     """
#     _name_prefix = "GACDC_HT"
#     grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
#     heater_open = i3.BoolProperty(default=True, doc='False for no heater')
#     lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
#     # heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
#     # heater_length = i3.PositiveNumberProperty(default=730., doc="heater_length")
#     # m1_taper_width = i3.PositiveNumberProperty(default=10., doc="Width of the M1 contact")
#     # m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
#     # m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
#     # overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")
#
#
#     class Layout(i3.LayoutView):
#         def _generate_instances(self, insts):
#
#             insts_insts = {
#                 'GACDC': GACDCPhaseShiftApodized(gap=0.4,
#                                       lambda_resonance=self.lambda_resonance),
#                 # 'GACDC': GACDCPhaseShiftApodized(gap=0.4,
#                 #                       lambda_resonance=self.lambda_resonance),
#                 'TempPort': TempPort()
#                 # 'inarm': bend_in_out,
#                 # 'outarm': bend_in_out,
#                 # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
#                 # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
#             }
#
#             insts_specs = [
#                 # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
#                 i3.Place('GACDC:in', (0, 0), angle=180),
#                 # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
#                 # i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
#                 # i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
#             ]
#             if self.heater_open:
#                 insts_insts['heater'] = custom_elec_single(m1_taper_width=10,)
#                 insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'GACDC:in', (-11, -9.88)))
#
#             insts += i3.place_and_route(
#                 insts=insts_insts,
#                 specs=insts_specs
#             )
#             return insts
#
#         def _generate_ports(self, ports):
#             ports += i3.expose_ports(self.instances,
#                                      {
#                                          'GACDC:in': 'in',
#                                          'GACDC:through': 'through',
#                                          'GACDC:drop': 'drop',
#                                          'GACDC:add': 'add',
#                                          # 'heater:elec1': 'elec2',
#                                          # 'heater:elec2': 'elec1',
#                                      })
#             if self.heater_open:
#                 ports += i3.expose_ports(self.instances,
#                                          {
#                                              'heater:elec1': 'elec2',
#                                              'heater:elec2': 'elec1',
#                                          })
#             return ports


tt1 = pdk.SiWireWaveguideTemplate()
tt1.Layout(core_width=0.64)
tt2 = pdk.SiWireWaveguideTemplate()
tt2.Layout(core_width=0.41)

class GACDC_HT(i3.PCell):
    """
    ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
    端口与“GACDCPhaseShiftApodized”的端口设置有区别，因为旋转了180度
    →   in      ---------------------------------    through  →
    ←   drop    ---------------------------------    add    ←
    """
    _name_prefix = "GACDC_HT"
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
    gap = i3.PositiveNumberProperty(default=0.38, doc="The gap between two waveguides.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
                                                                              "on the bus waveguide.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
                                                                               "on the drop waveguide.")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")
    #
    # tt1 = pdk.SiWireWaveguideTemplate(),
    #
    # tt2 = i3.TraceTemplateProperty(
    #     default=pdk.SiWireWaveguideTemplate(),
    #     doc="Trace template of the access waveguide"
    # )
    # tt1 = pdk.SiWireWaveguideTemplate()
    # tt1.Layout(core_width=0.41)
    # tt2 = pdk.SiWireWaveguideTemplate()
    # tt2.Layout(core_width=0.41)


    # heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
    # heater_length = i3.PositiveNumberProperty(default=730., doc="heater_length")
    # m1_taper_width = i3.PositiveNumberProperty(default=10., doc="Width of the M1 contact")
    # m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
    # m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    # overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")


    class Layout(i3.LayoutView):

        def _generate_instances(self, insts):
            Sbend1 = WaveguideSBend(trace_template=tt1, radius=12, x_offset=30, y_offset=9.5)
            Sbend2 = WaveguideSBend(trace_template=tt2, radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {
                # 'GACDC': GACDCPhaseShiftApodized(grating_period=self.grating_period,
                #                                  num_period=self.num_period,
                #                                  grating_width_bus_waveguide=self.grating_width_bus_waveguide,
                #                                  grating_width_drop_waveguide=self.grating_width_drop_waveguide,
                #                                  num_side=self.num_side,
                #                                  w_bus=self.w_bus,
                #                                  w_drop=self.w_drop,
                #                                  gap=self.gap),
                'GACDC': GACDCPhaseShiftApodized(gap=self.gap,
                                                 lambda_resonance=self.lambda_resonance),
                'Sbend_in': Sbend1,
                'Sbend_drop': Sbend2,
                'Sbend_add': Sbend2,
                'Sbend_through': Sbend1,
                'TempPort': TempPort(),
                'Taper_in': Taper_TempPort1(width=0.64),
                'Taper_through': Taper_TempPort1(width=0.64),
                'Taper_add': Taper_TempPort2(width=0.41),
                'Taper_drop': Taper_TempPort2(width=0.41),
                'Port2': TempPort2(),
                # 'inarm': bend_in_out,
                # 'outarm': bend_in_out,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                i3.FlipH('GACDC'),
                i3.FlipV('GACDC'),
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.PlaceRelative('Sbend_in:out', 'GACDC:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'GACDC:drop', (0, 0)),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),

                i3.PlaceRelative('Taper_in:in', 'Sbend_in:in', (0, 0), angle=0),
                i3.PlaceRelative('Taper_drop:in', 'Sbend_drop:in', (0, 0), angle=0),

                i3.PlaceRelative('Taper_add:in', 'Sbend_add:out', (0, 0), angle=180),
                i3.PlaceRelative('Taper_through:in', 'Sbend_through:out', (0, 0), angle=180),
                # i3.Place('Taper_in:in', (10, 0)),
                # i3.Place('Sbend_test:in', (30, 0)),
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('GACDC:in', (0, 0), angle=180),

                i3.PlaceRelative('Port2:in', 'Taper_add:out',  (12, -12), angle=90),
                i3.ConnectManhattan('Port2:in', 'Taper_add:out')
                # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
                # i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
                # i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10,)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'GACDC:in', (5, -0.38)))


            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Taper_in:out': 'in',
                                         'Taper_through:out': 'through',
                                         'Taper_drop:out': 'drop',
                                         'Taper_add:out': 'add',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports

class GACDC_HT_1(i3.PCell):
    """
    ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
    端口与“GACDCPhaseShiftApodized”的端口设置有区别，因为旋转了180度
    →   in      ---------------------------------    through  →
    ←   drop    ---------------------------------    add    ←
    """
    _name_prefix = "GACDC_HT_1"
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    w_bus = i3.PositiveNumberProperty(default=0.6, doc="Width of the bus waveguide, act as input.")
    w_drop = i3.PositiveNumberProperty(default=0.35, doc="Width of the drop waveguide, act as output")
    gap = i3.PositiveNumberProperty(default=0.38, doc="The gap between two waveguides.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.04, doc="The width of grating"
                                                                              "on the bus waveguide.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.06, doc="The width of grating"
                                                                               "on the drop waveguide.")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    num_period = i3.PositiveNumberProperty(default=2500, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=12, doc="apodization strength.")
    #
    # tt1 = pdk.SiWireWaveguideTemplate(),
    #
    # tt2 = i3.TraceTemplateProperty(
    #     default=pdk.SiWireWaveguideTemplate(),
    #     doc="Trace template of the access waveguide"
    # )
    # tt1 = pdk.SiWireWaveguideTemplate()
    # tt1.Layout(core_width=0.41)
    # tt2 = pdk.SiWireWaveguideTemplate()
    # tt2.Layout(core_width=0.41)


    # heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
    # heater_length = i3.PositiveNumberProperty(default=730., doc="heater_length")
    # m1_taper_width = i3.PositiveNumberProperty(default=10., doc="Width of the M1 contact")
    # m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
    # m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    # overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")


    class Layout(i3.LayoutView):

        def _generate_instances(self, insts):
            Sbend1 = WaveguideSBend(trace_template=tt1, radius=12, x_offset=30, y_offset=9.5)
            Sbend2 = WaveguideSBend(trace_template=tt2, radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {
                # 'GACDC': GACDCPhaseShiftApodized(grating_period=self.grating_period,
                #                                  num_period=self.num_period,
                #                                  grating_width_bus_waveguide=self.grating_width_bus_waveguide,
                #                                  grating_width_drop_waveguide=self.grating_width_drop_waveguide,
                #                                  num_side=self.num_side,
                #                                  w_bus=self.w_bus,
                #                                  w_drop=self.w_drop,
                #                                  gap=self.gap),
                'GACDC': GACDCPhaseShiftApodized(gap=0.38,
                                                 lambda_resonance=self.lambda_resonance),
                'Sbend_in': Sbend1,
                'Sbend_drop': Sbend2,
                'Sbend_add': Sbend2,
                'Sbend_through': Sbend1,
                'TempPort': TempPort(),
                'Taper_in': Taper_TempPort1(width=0.64),
                'Taper_through': Taper_TempPort1(width=0.64),
                'Taper_add': Taper_TempPort2(width=0.41),
                'Taper_drop': Taper_TempPort2(width=0.41),
                # 'Port2': TempPort2(),
                # 'inarm': bend_in_out,
                # 'outarm': bend_in_out,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                i3.FlipH('GACDC'),
                i3.FlipV('GACDC'),
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.PlaceRelative('Sbend_in:out', 'GACDC:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'GACDC:drop', (0, 0)),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),

                i3.PlaceRelative('Taper_in:in', 'Sbend_in:in', (0, 0), angle=0),
                i3.PlaceRelative('Taper_drop:in', 'Sbend_drop:in', (0, 0), angle=0),

                i3.PlaceRelative('Taper_add:in', 'Sbend_add:out', (0, 0), angle=180),
                i3.PlaceRelative('Taper_through:in', 'Sbend_through:out', (0, 0), angle=180),
                # i3.Place('Taper_in:in', (10, 0)),
                # i3.Place('Sbend_test:in', (30, 0)),
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('GACDC:in', (0, 0), angle=180),
                #
                # i3.PlaceRelative('Port2:in', 'Taper_add:out',  (12, -12), angle=90),
                # i3.ConnectManhattan('Port2:in', 'Taper_add:out')
                # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
                # i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
                # i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10,)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'GACDC:in', (5, -0.38)))


            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Taper_in:out': 'in',
                                         'Taper_through:out': 'through',
                                         'Taper_drop:out': 'drop',
                                         'Taper_add:out': 'add',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports


class GACDC_HT_ScanField(i3.PCell):
    """
    adjust port length to EBL scan field
    ports:2x2 端口设置示意如下（下面的是宽波导，宽度600nm，上面是窄波导，宽度350nm）
    端口与“GACDCPhaseShiftApodized”的端口设置有区别，因为旋转了180度
    →   in      ---------------------------------    through  →
    ←   drop    ---------------------------------    add    ←
    """
    _name_prefix = "GACDC_HT_ScanField"
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="gap between components")
    grating_period = i3.PositiveNumberProperty(default=0.33, doc="The period of the GACDC.")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    # heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
    # heater_length = i3.PositiveNumberProperty(default=730., doc="heater_length")
    # m1_taper_width = i3.PositiveNumberProperty(default=10., doc="Width of the M1 contact")
    # m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
    # m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    # overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")


    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'GACDC': GACDCPhaseShiftApodized(lambda_resonance=self.lambda_resonance),
                # 'TempPort_in': TempPort(),
                # 'TempPort_drop': TempPort(),
                'TempPort_through': TempPort(),
                'TempPort_add': TempPort(),
                'TempPort_in': TempPort(),
                'Sbend_in': Sbend,
                'Sbend_drop': Sbend,
                'Sbend_add': Sbend,
                'Sbend_through': Sbend,
                # 'inarm': bend_in_out,
                # 'outarm': bend_in_out,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.FlipH('GACDC'),
                i3.FlipV('GACDC'),
                i3.Place('TempPort_in:in', (0, 0)),
                i3.PlaceRelative('Sbend_in:in', 'TempPort_in:in', (EBL_scan_filed_length/20, 0)),
                # i3.Place('Sbend_drop:in', (0, 0)),
                i3.FlipV('Sbend_in'),
                i3.FlipV('Sbend_add'),
                i3.PlaceRelative('Sbend_in:out', 'GACDC:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'GACDC:drop', (0, 0)),
                i3.PlaceRelative('Sbend_through:in', 'GACDC:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'GACDC:add', (0, 0)),
                # i3.Place('TempPort_drop:in', (0, 0)),
                # i3.PlaceRelative('GACDC:drop', 'TempPort_drop:in', (0, 0)),
                # i3.PlaceRelative('TempPort_in:in', 'GACDC:in', (0, 0)),
                i3.PlaceRelative('TempPort_add:in', 'Sbend_drop:in',
                                 (EBL_scan_filed_length - EBL_scan_filed_length/20, 0)),
                i3.PlaceRelative('TempPort_through:in', 'TempPort_in:in', (EBL_scan_filed_length, 0)),
                i3.ConnectManhattan([
                    ('Sbend_in:in', 'TempPort_in:out'),
                    ('TempPort_through:in', 'Sbend_through:out'),
                ])
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10,)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'GACDC:in', (19, -0.38)))

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'TempPort_in:in': 'in',
                                         'TempPort_through:out': 'through',
                                         'Sbend_drop:in': 'drop',
                                         'Sbend_add:out': 'add',
                                         # # 'heater:elec1': 'elec2',
                                         # # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports


class GACDCFourChannel(i3.PCell):
    """
    Four channel GACDC output, occupying two EBL scan fields
    """
    _name_prefix = "GACDCFourChannel"
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="gap between components")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda.")
    gap_y = i3.PositiveNumberProperty(default=100, doc="desired resonance lambda.")
    gap_x = i3.PositiveNumberProperty(default=30, doc="desired resonance lambda.")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            gap_y = self.gap_y
            gap_x = self.gap_x
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'GACDC_signal_1': GACDC_HT(lambda_resonance=lambda_signal_1),
                'GACDC_signal_2': GACDC_HT(lambda_resonance=lambda_signal_2),
                'GACDC_idler_1': GACDC_HT(lambda_resonance=lambda_idler_1),
                'GACDC_idler_2': GACDC_HT(lambda_resonance=lambda_idler_2),
                # 'crossing': pdk.CrossX(),
                'port_signal_1': TempPort(),
                'port_signal_2': TempPort(),
                'port_idler_1': TempPort(),
                'port_idler_2': TempPort(),
                'port_in': TempPort(),
                'port_through': TempPort()
            }
            insts_specs = [
                i3.Place('port_in:in', (0, 0)),
                i3.PlaceRelative('GACDC_signal_1:in', 'port_in:out', (20, 0)),

                i3.PlaceRelative('GACDC_signal_2:in', 'GACDC_signal_1:in', (EBL_scan_filed_length + 45, 100)),

                i3.FlipV('GACDC_idler_1'),
                i3.PlaceRelative('GACDC_idler_1:in', 'GACDC_signal_2:in', (EBL_scan_filed_length + 45, 100)),

                i3.FlipV('GACDC_idler_2'),
                i3.PlaceRelative('GACDC_idler_2:in', 'GACDC_idler_1:in', (EBL_scan_filed_length + 45, 100)),

                i3.PlaceRelative('port_through:in', 'GACDC_idler_2:through', (20, 0)),
                i3.PlaceRelative('port_signal_1:in', 'port_through:in', (0, -400)),
                i3.PlaceRelative('port_signal_2:in', 'port_through:in', (0, -300)),
                i3.PlaceRelative('port_idler_1:in', 'port_through:in', (0, 200)),
                i3.PlaceRelative('port_idler_2:in', 'port_through:in', (0, 100)),
                i3.ConnectManhattan([
                        ('GACDC_signal_1:in', 'port_in:out'),
                        ('GACDC_signal_2:in', 'GACDC_signal_1:through'),
                        ('GACDC_idler_1:in', 'GACDC_signal_2:through'),
                        # ('GACDC_idler_2:in', 'GACDC_idler_1:through'),
                        ('GACDC_signal_1:drop', 'port_signal_1:in'),
                        ('GACDC_signal_2:drop', 'port_signal_2:in'),
                        # ('GACDC_idler_1:drop', 'port_idler_1:in'),
                        ('GACDC_idler_2:drop', 'port_idler_2:in'),
                        ('GACDC_idler_2:through', 'port_through:in'),
                    ],
                bend_radius=20,
                ),
                i3.ConnectManhattan(
                    [
                        ("GACDC_idler_1:drop", 'port_idler_1:in'),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (700, 100), i3.START + (750, 200)]
                ),
                i3.ConnectManhattan(
                    [
                        ('GACDC_idler_1:through', 'GACDC_idler_2:in'),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (30, 30)]
                ),
                # # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                # i3.Place('port_in:in', (0, gap_y * 2)),
                # # i3.PlaceRelative('port_through:in', 'port_in:in', (0, gap_y * 3)),
                # i3.Place('port_signal_1:in', (EBL_scan_filed_length, gap_y)),
                # i3.Place('port_signal_2:in', (EBL_scan_filed_length, gap_y * 4)),
                # i3.Place('port_idler_1:in', (EBL_scan_filed_length, gap_y * 8)),
                # i3.Place('port_through:in', (EBL_scan_filed_length, gap_y * 7)),
                # i3.Place('port_idler_2:in', (EBL_scan_filed_length, gap_y * 6)),
                # i3.PlaceRelative('GACDC_signal_1:in', 'port_in:in', (gap_x*2, 0)),
                # i3.FlipH('GACDC_signal_2'),
                # i3.FlipV('GACDC_signal_2'),
                # i3.PlaceRelative('GACDC_signal_2:in', 'GACDC_signal_1:through', (0, gap_y)),
                # i3.FlipV('GACDC_idler_1'),
                # i3.PlaceRelative('GACDC_idler_1:in', 'GACDC_signal_2:through', (0, gap_y)),
                # i3.FlipH('GACDC_idler_2'),
                # i3.FlipV('GACDC_idler_2'),
                # i3.PlaceRelative('GACDC_idler_2:in', 'GACDC_idler_1:through', (0, gap_y)),
                # # i3.PlaceRelative('crossing:out1', 'GACDC_idler_2:through', (-gap_x / 3, 0)),
                # i3.ConnectManhattan([
                #     ('GACDC_signal_1:in', 'port_in:out'),
                #     ('GACDC_signal_2:in', 'GACDC_signal_1:through'),
                #     ('GACDC_idler_1:in', 'GACDC_signal_2:through'),
                #     ('GACDC_idler_2:in', 'GACDC_idler_1:through'),
                #     # ('crossing:out1', 'GACDC_idler_2:through'),
                #     # ('GACDC_idler_1:drop', 'crossing:in2'),
                #     # ('crossing:out2', 'port_idler_1:in'),
                #     ('GACDC_idler_2:drop', 'port_idler_2:in'),
                #     ('GACDC_signal_1:drop', 'port_signal_1:in'),
                #     ('GACDC_signal_2:drop', 'port_signal_2:in'),
                #     # ('crossing:in1', 'port_through:out'),
                #     # ('TempPort_through:in', 'Sbend_through:out'),
                # ]),
                # i3.ConnectManhattan(
                #     [
                #         ("GACDC_idler_1:drop", "port_idler_1:in"),
                #     ],
                #     bend_radius=10,
                #     control_points=[i3.V(20)]
                # ),
                # i3.ConnectManhattan(
                #     [
                #         ("GACDC_idler_2:through", "port_through:in"),
                #     ],
                #     bend_radius=10,
                #     control_points=[i3.V(30)]
                # ),
            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'port_in:in': 'in',
                                         'port_through:out': 'through',
                                         'port_signal_1:out': 'signal_1',
                                         'port_signal_2:out': 'signal_2',
                                         'port_idler_1:out': 'idler_1',
                                         'port_idler_2:out': 'idler_2',
                                         # # 'heater:elec1': 'elec2',
                                         # # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'GACDC_signal_1:elec1': 'elec1',
                                             'GACDC_signal_1:elec2': 'elec2',
                                             'GACDC_signal_2:elec1': 'elec4',
                                             'GACDC_signal_2:elec2': 'elec3',
                                             'GACDC_idler_1:elec1': 'elec5',
                                             'GACDC_idler_1:elec2': 'elec6',
                                             'GACDC_idler_2:elec1': 'elec8',
                                             'GACDC_idler_2:elec2': 'elec7',
                                         })
            return ports


if __name__ == '__main__':
    # pass
    # lo = GACDCPhaseShiftApodized()
    # lo = GACDC_HT_ScanField()
    lo2 = GACDC_HT()
    lo = GACDCFourChannel()
    # lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('GACDCFourChannel_test.gds')

    lo3 = Taper_TempPort1()
    lo3.Layout().write_gdsii('Taper_TempPort1.gds')
    lo2.Layout().write_gdsii('GACDC_HT.gds')
    lo3 = GACDCPhaseShiftApodized()
    lo3.Layout().write_gdsii('GACDCPhaseShiftApodized.gds')
    # lamb = [1.55817, 1.55575, 1.55252, 1.54932, 1.54692]
    lamb = [1.534, 1.542, 1.550, 1.558, 1.54692]
    for i in range(5):
        print(lambda_to_period(lamb[i]))
