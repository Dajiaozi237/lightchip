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


class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
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

class custom_elec_single(i3.PCell):
    _name_prefix = "custom_elec"
    heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
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


tt3 = pdk.SiWireWaveguideTemplate()
tt3.Layout(core_width=0.339)

tt4 = pdk.SiWireWaveguideTemplate()
tt4.Layout(core_width=0.439)

tt1 = pdk.SiWireWaveguideTemplate()
tt1.Layout(core_width=0.33)
tt2 = pdk.SiWireWaveguideTemplate()
tt2.Layout(core_width=0.43)


class Broad_WidthChirp_GuassApodized(i3.PCell):
    """
    broad add bus filter based on grating
    apply Guass phase-shift apodization

    ports:2x2 端口设置示意如下（上面的是宽波导，宽度570nm，下面是窄波导，宽度430nm）
    """
    #←   drop      ---------------------------------    add    ←
    #→   in    ---------------------------------    through   →
    """

    波导的宽度随光栅的数目变化呈现阶梯型增加，周期不变
    宽带起始波长和截至波长与模式耦合有关

    默认gap140nm，长度约320μm，带宽约20nm
    """
    _name_prefix = "broadbandfilter"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_drop = i3.PositiveNumberProperty(default=0.57, doc="Width of the drop waveguide, act as input.")
    w_bus = i3.PositiveNumberProperty(default=0.43, doc="Width of the bus waveguide, act as output")
    chirp_num=i3.PositiveNumberProperty(default=100, doc="chirp rate of the waveguide width")
    chirp_ladder_num=i3.PositiveNumberProperty(default=10, doc="chirp ladder num of the waveguide width")
    gap = i3.PositiveNumberProperty(default=0.1, doc="The gap between two waveguides.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.16, doc="The width of grating"
                                                                              "on the drop waveguide.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.14, doc="The width of grating"
                                                                               "on the bus waveguide.")
    grating_period = i3.PositiveNumberProperty(default=0.325, doc="The period of the filter.")
    num_period = i3.PositiveNumberProperty(default=1000, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=14, doc="apodization strength.")
    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            grating_position=0
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            chirp_num=self.chirp_num
            chirp_ladder_num=self.chirp_ladder_num
            grating_period = self.grating_period
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
            # 'in' port
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, gap / 2 +w_drop / 2+grating_width_drop_waveguide / 2),
                box_size=(5, w_drop-grating_width_drop_waveguide),
            )
            # 'bus' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(0.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
            #     end_coord=(15.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
            #     begin_width=core_width,
            #     end_width=w_bus-grating_width_bus_waveguide,
            # )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, -gap / 2 - w_bus / 2-grating_width_bus_waveguide/2),
                box_size=(5, w_bus-grating_width_bus_waveguide),
            )
            for j in range(int(chirp_ladder_num)):
                for i in range(j*int(chirp_num),j*int(chirp_num)+int(chirp_num)):
                    w_bus_chirp= w_bus + j * 0.001 - grating_width_bus_waveguide
                    w_drop_chirp = w_drop + j * 0.001 - grating_width_drop_waveguide
                    # the drop waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20+grating_position+grating_period/2,gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                        box_size=(grating_period, w_drop_chirp),
                    )
                    # the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + grating_position+grating_period/2, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                        box_size=(grating_period, w_bus_chirp),
                    )
                    # add gratings
                    # upside of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (-0.25 + i) * grating_period +
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength)),
                                gap / 2 + grating_width_drop_waveguide*3/2+w_drop_chirp),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # down of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period +
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength)),
                                gap / 2 + grating_width_drop_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # upside of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.75 + i) * grating_period,
                                -gap / 2 - grating_width_bus_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    # down of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period,
                                -gap / 2 - w_bus_chirp - grating_width_bus_waveguide *3/ 2),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    grating_position=grating_position+grating_period

            # Cladding
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, (w_bus - w_drop) / 4),
                end_coord=(40 + coupling_length, (w_bus - w_drop) / 4),
                begin_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
                end_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
            )
            # add additional part, length=5
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position + 2.5, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                box_size=(5, w_bus_chirp),
            )

            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position  + 2.5, gap / 2 +grating_width_drop_waveguide+ w_drop_chirp / 2),
                box_size=(5, w_drop_chirp),
            )
            # # 'add' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(25 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
            #     end_coord=(40 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
            #     begin_width=w_bus_chirp,
            #     end_width=core_width,
            # )
            # # 'through' port
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(25 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
            #     end_coord=(40 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
            #     begin_width=w_drop_chirp,
            #     end_width=core_width,
            # )
            return elems

        def _generate_ports(self, ports):
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            grating_period = self.grating_period
            num_period = self.num_period
            coupling_length = grating_period * num_period
            trace_template = self.trace_template
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            w_bus_chirp = w_bus + 9 * 0.001 - grating_width_bus_waveguide
            w_drop_chirp = w_drop + 9 * 0.001 - grating_width_drop_waveguide
            ports += i3.OpticalPort(
                name="drop",
                position=(15, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="add",
                position=(25 + coupling_length, gap / 2 +grating_width_drop_waveguide+ w_drop_chirp / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="through",
                position=(25 + coupling_length, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="in",
                position=(15, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            return ports


class Broad_WidthChirp_GuassApodized_HT(i3.PCell):
    """
    ports:2x2 端口设置示意如下（上面的是宽波导，宽度570nm，下面是窄波导，宽度430nm）
    """
    #←   drop      ---------------------------------    add    ←
    #→   in    ---------------------------------    through   →
    """
    """
    #需要翻转一下
    #BF:broad filter

    _name_prefix = "Broad_WidthChirp_GuassApodized_HT"
    grating_period = i3.PositiveNumberProperty(default=0.32, doc="The period of the filter.")
    gap = i3.PositiveNumberProperty(default=0.14, doc="The gap between two waveguides.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                          "drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.14, doc="The width of grating"
                                                                               "on the drop waveguide.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                         "the bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.1, doc="The width of grating"
                                                                             "on the bus waveguide.")
    class Layout(i3.LayoutView):

        def _generate_instances(self, insts):
            gap = self.gap
            grating_period = self.grating_period
            grating_width_drop_waveguide=self.grating_width_drop_waveguide
            grating_width_bus_waveguide=self.grating_width_bus_waveguide

            Sbend1 = WaveguideSBend(trace_template=tt1, radius=12, x_offset=30, y_offset=9.5)
            Sbend2 = WaveguideSBend(trace_template=tt2, radius=12, x_offset=30, y_offset=9.5)
            Sbend3 = WaveguideSBend(trace_template=tt3, radius=12, x_offset=30, y_offset=9.5)
            Sbend4 = WaveguideSBend(trace_template=tt4, radius=12, x_offset=30, y_offset=9.5)
            insts_insts = {

                'BF': Broad_WidthChirp_GuassApodized(grating_period=grating_period,
                                                     gap=gap,
                                                     grating_width_drop_waveguide=grating_width_drop_waveguide,
                                                     grating_width_bus_waveguide=grating_width_bus_waveguide,
                                                    ),
                'Sbend_in': Sbend1,
                'Sbend_drop': Sbend2,
                'Sbend_add': Sbend4,
                'Sbend_through': Sbend3,
                'TempPort': TempPort(),
                'Taper_in': Taper_TempPort1(width=0.33),
                'Taper_through': Taper_TempPort1(width=0.339),
                'Taper_add': Taper_TempPort2(width=0.439),
                'Taper_drop': Taper_TempPort2(width=0.43),
            }

            insts_specs = [

                i3.FlipV('Sbend_drop'),
                i3.PlaceRelative('Sbend_in:out', 'BF:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'BF:drop', (0, 0)),
                i3.FlipV('Sbend_through'),
                i3.PlaceRelative('Sbend_through:in', 'BF:through', (0, 0)),
                i3.PlaceRelative('Sbend_add:in', 'BF:add', (0, 0)),

                i3.PlaceRelative('Taper_in:in', 'Sbend_in:in', (0, 0), angle=0),
                i3.PlaceRelative('Taper_drop:in', 'Sbend_drop:in', (0, 0), angle=0),

                i3.PlaceRelative('Taper_add:in', 'Sbend_add:out', (0, 0), angle=180),
                i3.PlaceRelative('Taper_through:in', 'Sbend_through:out', (0, 0), angle=180),

                i3.Place('BF:in', (0, 0)),

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
                                         'Taper_in:out': 'in',
                                         'Taper_through:out': 'through',
                                         'Taper_drop:out': 'drop',
                                         'Taper_add:out': 'add',
                                     })
            return ports
class Broad_WidthChirp_GuassApodized_HT_ScanField(i3.PCell):
    """
    adjust port length to EBL scan field
    ports:2x2 端口设置示意如下（上面的是宽波导，宽度570nm，下面是窄波导，宽度430nm）
    """
    #←   drop      ---------------------------------    add    ←
    #→   in    ---------------------------------    through   →

    _name_prefix = "Broad_WidthChirp_GuassApodized_HT_ScanField"
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="gap between components")
    grating_period = i3.PositiveNumberProperty(default=0.32, doc="The period of the BF.")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            Sbend = WaveguideSBend(trace_template=SiWireWaveguideTemplate(), radius=12, x_offset=30, y_offset=9.5)
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'BF': Broad_WidthChirp_GuassApodized(),
                'TempPort_through': TempPort(),
                'TempPort_add': TempPort(),
                'TempPort_in': TempPort(),
                'Sbend_in': Sbend,
                'Sbend_drop': Sbend,
                'Sbend_through': Sbend,
            }
            insts_specs = [
                i3.Place('TempPort_in:in', (0, 0)),
                i3.PlaceRelative('Sbend_in:in', 'TempPort_in:in', (EBL_scan_filed_length / 20, 0)),
                i3.FlipV('Sbend_drop'),
                i3.PlaceRelative('Sbend_in:out', 'BF:in', (0, 0)),
                i3.PlaceRelative('Sbend_drop:out', 'BF:drop', (0, 0)),
                i3.FlipV('Sbend_through'),
                i3.PlaceRelative('Sbend_through:in', 'BF:through', (0, 0)),
                # i3.PlaceRelative('Sbend_add:in', 'BF:add', (0, 0)),
                # i3.PlaceRelative('TempPort_add:in', 'Sbend_drop:in',
                #                  (EBL_scan_filed_length - EBL_scan_filed_length / 20, 0)),
                i3.PlaceRelative('TempPort_through:in', 'TempPort_in:in', (EBL_scan_filed_length, 0)),
                i3.ConnectManhattan([
                    ('Sbend_in:in', 'TempPort_in:out'),
                    # ('TempPort_through:in', 'Sbend_through:out'),
                ])
            ]
            # if self.heater_open:
            #     insts_insts['heater'] = custom_elec_single(m1_taper_width=10, )
            #     insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'BCAF:in', (19, -0.38)))

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
                                     'Sbend_bus:in': 'bus',
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
class Broad_WidthChirp_fanGuassApodized(i3.PCell):
    """
    broad add bus filter based on grating
    apply Guass phase-shift apodization

    ports:2x2 端口设置示意如下（下面的是宽波导，宽度570nm，上面是窄波导，宽度430nm）
    """
    #→   in      ---------------------------------    through  →
    #←   bus    ---------------------------------    add    ←
    """

    波导的宽度随光栅的数目变化呈现阶梯型增加，周期不变
    宽带起始波长和截至波长与模式耦合有关

    默认gap140nm，长度约320μm，带宽约20nm
    """
    _name_prefix = "broadbandfilter"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_drop = i3.PositiveNumberProperty(default=0.43, doc="Width of the drop waveguide, act as input.")
    w_bus = i3.PositiveNumberProperty(default=0.57, doc="Width of the bus waveguide, act as output")
    chirp_num=i3.PositiveNumberProperty(default=100, doc="chirp rate of the waveguide width")
    chirp_ladder_num=i3.PositiveNumberProperty(default=10, doc="chirp ladder num of the waveguide width")
    gap = i3.PositiveNumberProperty(default=0.14, doc="The gap between two waveguides.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.1, doc="The width of grating"
                                                                              "on the drop waveguide.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.14, doc="The width of grating"
                                                                               "on the bus waveguide.")
    grating_period = i3.PositiveNumberProperty(default=0.32, doc="The period of the filter.")
    num_period = i3.PositiveNumberProperty(default=1000, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=14, doc="apodization strength.")
    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            grating_position=0
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            chirp_num=self.chirp_num
            chirp_ladder_num=self.chirp_ladder_num
            grating_period = self.grating_period
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
            # 'in' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                end_coord=(15.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                begin_width=core_width,
                end_width=w_drop-grating_width_drop_waveguide,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, gap / 2 +  w_drop/2+grating_width_drop_waveguide / 2),
                box_size=(5, w_drop-grating_width_drop_waveguide),
            )
            # 'bus' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                end_coord=(15.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                begin_width=core_width,
                end_width=w_bus-grating_width_bus_waveguide,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                box_size=(5, w_bus-grating_width_bus_waveguide),
            )
            for j in range(int(chirp_ladder_num)):
                for i in range(j*int(chirp_num),j*int(chirp_num)+int(chirp_num)):
                    w_bus_chirp= w_bus + j * 0.001 - grating_width_bus_waveguide
                    w_drop_chirp = w_drop + j * 0.001 - grating_width_drop_waveguide
                    # the drop waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20+grating_position+grating_period/2,gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                        box_size=(grating_period, w_drop_chirp),
                    )
                    # the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + grating_position+grating_period/2, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                        box_size=(grating_period, w_bus_chirp),
                    )
                    # add gratings
                    # upside of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (-0.25 + i) * grating_period +
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength)),
                                gap / 2 + grating_width_drop_waveguide*3/2+w_drop_chirp),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # down of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period +
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength)),
                                gap / 2 + grating_width_drop_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # upside of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period,
                                -gap / 2 - grating_width_bus_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    # down of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.75 + i) * grating_period,
                                -gap / 2 - w_bus_chirp - grating_width_bus_waveguide *3/ 2),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    grating_position=grating_position+grating_period

            # Cladding
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, (w_bus - w_drop) / 4),
                end_coord=(40 + coupling_length, (w_bus - w_drop) / 4),
                begin_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
                end_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
            )
            # add additional part, length=5
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position + 2.5, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                box_size=(5, w_bus_chirp),
            )

            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position  + 2.5, gap / 2 +grating_width_drop_waveguide+ w_drop_chirp / 2),
                box_size=(5, w_drop_chirp),
            )
            # 'add' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                end_coord=(40 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                begin_width=w_bus_chirp,
                end_width=core_width,
            )
            # 'through' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                end_coord=(40 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                begin_width=w_drop_chirp,
                end_width=core_width,
            )
            return elems
        def _generate_ports(self, ports):
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            grating_period = self.grating_period
            num_period = self.num_period
            coupling_length = grating_period * num_period
            trace_template = self.trace_template
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            w_bus_chirp = w_bus + 9 * 0.001 - grating_width_bus_waveguide
            w_drop_chirp = w_drop + 9 * 0.001 - grating_width_drop_waveguide
            ports += i3.OpticalPort(
                name="in",
                position=(0.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="through",
                position=(40 + coupling_length, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="add",
                position=(40 + coupling_length, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="bus",
                position=(0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            return ports
class Broad_WidthChirp_fanGuassApodized_phasecompensation(i3.PCell):
    """
    broad add bus filter based on grating
    apply Guass phase-shift apodization

    ports:2x2 端口设置示意如下（下面的是宽波导，宽度570nm，上面是窄波导，宽度430nm）
    """
    #→   in      ---------------------------------    through  →
    #←   bus    ---------------------------------    add    ←
    """

    波导的宽度随光栅的数目变化呈现阶梯型增加，周期不变
    宽带起始波长和截至波长与模式耦合有关

    默认gap140nm，长度约320μm，带宽约20nm
    """
    _name_prefix = "broadbandfilter"
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    w_drop = i3.PositiveNumberProperty(default=0.43, doc="Width of the drop waveguide, act as input.")
    w_bus = i3.PositiveNumberProperty(default=0.57, doc="Width of the bus waveguide, act as output")
    chirp_num=i3.PositiveNumberProperty(default=100, doc="chirp rate of the waveguide width")
    chirp_ladder_num=i3.PositiveNumberProperty(default=10, doc="chirp ladder num of the waveguide width")
    gap = i3.PositiveNumberProperty(default=0.14, doc="The gap between two waveguides.")
    add_grating_drop_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on the "
                                                                         "drop waveguide.")
    grating_width_drop_waveguide = i3.PositiveNumberProperty(default=0.1, doc="The width of grating"
                                                                              "on the drop waveguide.")
    add_grating_bus_waveguide = i3.PositiveNumberProperty(default=1, doc="whether add grating on "
                                                                          "the bus waveguide.")
    grating_width_bus_waveguide = i3.PositiveNumberProperty(default=0.14, doc="The width of grating"
                                                                               "on the bus waveguide.")
    grating_period = i3.PositiveNumberProperty(default=0.32, doc="The period of the filter.")
    num_period = i3.PositiveNumberProperty(default=1000, doc="The number of periods i.e. the coupling length.")
    num_side = i3.PositiveNumberProperty(default=2, doc="on how many sides of the waveguide.")
    apodization_function = i3.StringProperty(default='Gaussian',
                                             doc="Apodization function: Gaussian")
    apodization_strength = i3.PositiveNumberProperty(default=14, doc="apodization strength.")
    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            grating_position=0
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            chirp_num=self.chirp_num
            chirp_ladder_num=self.chirp_ladder_num
            grating_period = self.grating_period
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
            # 'in' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                end_coord=(15.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                begin_width=core_width,
                end_width=w_drop-grating_width_drop_waveguide,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, gap / 2 +  w_drop/2+grating_width_drop_waveguide / 2),
                box_size=(5, w_drop-grating_width_drop_waveguide),
            )
            # 'bus' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                end_coord=(15.0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                begin_width=core_width,
                end_width=w_bus-grating_width_bus_waveguide,
            )
            elems += i3.Rectangle(
                layer=core_layer,
                center=(17.5, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                box_size=(5, w_bus-grating_width_bus_waveguide),
            )
            for j in range(int(chirp_ladder_num)):
                for i in range(j*int(chirp_num),j*int(chirp_num)+int(chirp_num)):
                    w_bus_chirp= w_bus + j * 0.001 - grating_width_bus_waveguide
                    w_drop_chirp = w_drop + j * 0.001 - grating_width_drop_waveguide
                    # the drop waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20+grating_position+grating_period/2,gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                        box_size=(grating_period, w_drop_chirp),
                    )
                    # the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + grating_position+grating_period/2, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                        box_size=(grating_period, w_bus_chirp),
                    )
                    # add gratings
                    # upside of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period,
                                gap / 2 + grating_width_drop_waveguide*3/2+w_drop_chirp),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # down of the drop waveguide, apply misalignment
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period +
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength)),
                                gap / 2 + grating_width_drop_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_drop_waveguide),
                    )
                    # upside of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period,
                                -gap / 2 - grating_width_bus_waveguide / 2),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    # down of the bus waveguide
                    elems += i3.Rectangle(
                        layer=core_layer,
                        center=(20 + (0.25 + i) * grating_period -
                                grating_period / 2 * (1 - mis_alignment(i, num_period, apodization_function,
                                                                        apodization_strength),
                                -gap / 2 - w_bus_chirp - grating_width_bus_waveguide *3/ 2)),
                        box_size=(grating_period / 2, grating_width_bus_waveguide),
                    )
                    grating_position=grating_position+grating_period

            # Cladding
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(0.0, (w_bus - w_drop) / 4),
                end_coord=(40 + coupling_length, (w_bus - w_drop) / 4),
                begin_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
                end_width=core_width + gap + (w_bus + w_drop) / 2 + 7.0,
            )
            # add additional part, length=5
            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position + 2.5, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                box_size=(5, w_bus_chirp),
            )

            elems += i3.Rectangle(
                layer=core_layer,
                center=(20 + grating_position  + 2.5, gap / 2 +grating_width_drop_waveguide+ w_drop_chirp / 2),
                box_size=(5, w_drop_chirp),
            )
            # 'add' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                end_coord=(40 + grating_position, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                begin_width=w_bus_chirp,
                end_width=core_width,
            )
            # 'through' port
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(25 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                end_coord=(40 + grating_position, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                begin_width=w_drop_chirp,
                end_width=core_width,
            )
            return elems
        def _generate_ports(self, ports):
            w_drop = self.w_drop
            w_bus = self.w_bus
            gap = self.gap
            grating_period = self.grating_period
            num_period = self.num_period
            coupling_length = grating_period * num_period
            trace_template = self.trace_template
            grating_width_drop_waveguide = self.grating_width_drop_waveguide
            grating_width_bus_waveguide = self.grating_width_bus_waveguide
            w_bus_chirp = w_bus + 9 * 0.001 - grating_width_bus_waveguide
            w_drop_chirp = w_drop + 9 * 0.001 - grating_width_drop_waveguide
            ports += i3.OpticalPort(
                name="in",
                position=(0.0, gap / 2 + w_drop/2+grating_width_drop_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="through",
                position=(40 + coupling_length, gap / 2 + grating_width_drop_waveguide+w_drop_chirp/ 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="add",
                position=(40 + coupling_length, -gap / 2 -grating_width_bus_waveguide- w_bus_chirp / 2),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="bus",
                position=(0, -gap / 2 - w_bus / 2-grating_width_bus_waveguide / 2),
                angle=180.0,
                trace_template=trace_template,
            )
            return ports

if __name__ == '__main__':
    # pass
    # lo = GACDCPhaseShiftApodized()
    # lo = GACDC_HT_ScanField()
    # lo = GACDC_HT()
    lo = Broad_WidthChirp_GuassApodized()
    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('Broad_WidthChirp_GuassApodized.gds')