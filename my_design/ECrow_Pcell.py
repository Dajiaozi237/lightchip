from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.technology import TECH
# from cell import EdgeCoupler
# from picazzo3.wg.bend import WgBend90
# import sys  # 导入sys模块
import numpy as np
TECH = pdk.TECH


# lo = pdk.EdgeCoupler()


class TextPCell(i3.PCell):
    # _name_prefix = "TextGC"
    text = i3.StringProperty(doc='display', default=' ')

    class Layout(i3.LayoutView):
        # n_rows = i3.IntProperty(doc="Number of GC rows", default=0)
        def _generate_elements(self, elems):
            labelText = self.text
            elems = i3.PolygonText(
                layer=TECH.PPLAYER.DOC,
                # layer=TECH.PPLAYER.NONE,
                text=labelText,
                alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                coordinate=(0, 0.),
                # font=0, height=30
                font=0, height=20
            )
            return elems

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name='LOC', position=(0, 0.), angle=0)
            return ports


class EdgeCoupler(i3.PCell):
    """
    edge coupler, with two-stage tapers
    stage1:
    width: 80nm-250nm, length: 90um
    stage2:
    width: 250nm-450nm, length: 60um
    """
    _name_prefix = "edge coupler"
    trace_template = i3.TraceTemplateProperty(doc="Trace template of the waveguide")
    taper1_length = i3.FloatProperty(default=90.0, doc="length of taper 1.")
    taper1_width = i3.PositiveNumberProperty(default=0.08, doc="width of taper 1.")
    taper2_length = i3.FloatProperty(default=60.0, doc="length of taper 2.")
    taper2_width = i3.PositiveNumberProperty(default=0.25, doc="width of taper 2.")
    etch_length = i3.PositiveNumberProperty(default=300.0, doc="length of the etch.")
    wg_length = i3.PositiveNumberProperty(default=10.0, doc="length of the output wg.")
    ssc_width = i3.PositiveNumberProperty(default=8.0, doc="width of leaky waveguide."
                                                           "real width: 6-7um")
    etch_width_SiO2 = i3.PositiveNumberProperty(default=40.0, doc="etching width of SiO2 layer.")


    def _default_trace_template(self):
        return pdk.SiWireWaveguideTemplate()

    def _default_SIO2_layer(self):
        return TECH.PPLAYER.EC_SIO2
        # return TECH.PPLAYER.SIO2.PP1

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            taper1_length = self.taper1_length
            taper1_width = self.taper1_width
            taper2_length = self.taper2_length
            taper2_width = self.taper2_width
            etch_width_SiO2 = self.etch_width_SiO2
            ssc_width = self.ssc_width
            # etching width of Si layer
            etch_width_Si = ssc_width + etch_width_SiO2 * 2 + 4
            etch_length = self.etch_length
            core_width = self.trace_template.core_width
            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer
            wg_length = self.wg_length


            """
            core layer
            two stage taper
            """
            # taper1 width: 80nm to 250nm, length: 90um
            # elems += i3.Wedge(
            #     layer=core_layer,
            #     begin_coord=(-taper1_length-taper2_length, 0.0),
            #     end_coord=(-taper2_length, 0.0),
            #     begin_width=taper1_width,
            #     end_width=taper2_width,
            # )
            # taper2 width: 250nm to 450nm, length: 60um
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(-taper2_length, 0.0),
                end_coord=(-0.0, 0.0),
                begin_width=taper2_width,
                end_width=core_width,
            )
            # 10um straight waveguide as output port, width 450nm
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(0.0, 0.0),
                end_coord=(wg_length, 0.0),
                begin_width=core_width,
                end_width=core_width,
            )
            """
            Cladding layer, the layer which defines Si etching
            """
            elems += i3.Wedge(
                layer=cladding_layer,
                begin_coord=(-etch_length, 0.0),
                end_coord=(wg_length, 0.0),
                begin_width=etch_width_Si,
                end_width=etch_width_Si,
            )
            """
            SiO2 etching layer
            """
            elems += i3.Wedge(
                # layer=TECH.PPLAYER.SIO2.PP1,
                layer=TECH.PPLAYER.EC_SIO2,
                begin_coord=(-etch_length, ssc_width / 2 + etch_width_SiO2 / 2),
                end_coord=(0.0, +ssc_width / 2 + etch_width_SiO2 / 2),
                begin_width=etch_width_SiO2,
                end_width=etch_width_SiO2,
            )
            elems += i3.Wedge(
                # layer=TECH.PPLAYER.SIO2.PP1,
                layer=TECH.PPLAYER.EC_SIO2,
                begin_coord=(-etch_length, -(ssc_width / 2 + etch_width_SiO2 / 2)),
                end_coord=(0.0, -(ssc_width / 2 + etch_width_SiO2 / 2)),
                begin_width=etch_width_SiO2,
                end_width=etch_width_SiO2,
            )

            return elems

        def _generate_ports(self, ports):
            trace_template = self.trace_template
            wg_length = self.wg_length

            ports += i3.OpticalPort(
                name="out",
                position=(wg_length, 0.0),
                angle=0.0,
                trace_template=trace_template,
            )

            return ports


class ECrow(i3.PCell):
    _name_prefix = "ECrow"
    # gap = i3.PositiveNumberProperty(default=10., doc="gap between grating coupler and device.")
    n_rows = i3.IntProperty(doc="Number of GC rows", default=20)
    EC = i3.ChildCellProperty(doc="EdgeCoupler cell", default=EdgeCoupler(taper2_length=200, taper2_width=0.08, ssc_width=6.5))
    ec_sep_y = i3.PositiveNumberProperty(doc="separation between the grating couplers", default=127.0)
    wg_str_len = i3.NonNegativeNumberProperty(doc="Length straight at the EC port", default=10.0)
    FA_marker_sep = i3.NonNegativeNumberProperty(default=3500., doc="separation of 2 alignment markers")
    FA_marker_width = i3.NonNegativeNumberProperty(default=50., doc="shape of FA_marker")
    FA_marker_length = i3.NonNegativeNumberProperty(default=300., doc="shape of FA_marker")
    # bd_radius = i3.NonNegativeNumberProperty(default=20, doc="bd_radius")
    textMarker = i3.BoolProperty(default=1, doc="show textMarker")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            bend_radius = 20
            insts_insts = {}
            insts_specs = []

            lo = self.EC.size_info()
            EC_width = lo.width

            for row in range(self.n_rows):
                wg = self.trace_template
                # wg.Layout(core_width=0.45, cladding_width=0.45 + 7)
                conn_wg = i3.RoundedWaveguide(trace_template=wg)
                conn_wg.Layout(
                    shape=[
                        (0.0, 0.0),
                        (-self.wg_str_len, 0.0),
                    ],
                )
                insts_insts["ec_{}".format(row)] = self.EC
                insts_insts["wg_{}".format(row)] = conn_wg
                if self.textMarker == 1:
                    insts_insts["text_{}".format(row)] = TextPCell(text=f'EC_{row+1}')

            alignrec = i3.LayoutCell().Layout(
                elements=[
                    i3.Rectangle(layer=TECH.PPLAYER.NONE,
                                 center=(self.FA_marker_width/2, 0),
                                 box_size=(self.FA_marker_length, self.FA_marker_width)),
                ]
            )
            insts_insts["align1"] = alignrec
            insts_insts["align2"] = alignrec

            for row in range(self.n_rows):
                y_loc = row * self.ec_sep_y
                # angle = 180.0 - self.gc.get_default_view(i3.LayoutView).ports['opt1'].angle
                angle = 0.0
                insts_specs.append(i3.Place("ec_{}:out".format(row), (0, y_loc), angle))
                insts_specs.append(i3.Place("wg_{}:in".format(row), (0, y_loc), 180.0))
                if self.textMarker == 1:
                    insts_specs.append(i3.PlaceRelative("text_{}:LOC".format(row), "ec_{}:out".format(row), (-50 - 70, -25-27)))
            y_loc = (self.n_rows-1) * self.ec_sep_y
            # print(y_loc)
            top_align_y = (self.FA_marker_sep - y_loc) / 2 + y_loc
            bot_align_y = 0 - (self.FA_marker_sep - y_loc) / 2
            # print(top_align_y,bot_align_y)
            # insts_specs.append(i3.PlaceRelative("align1", 'ec_0:out', (-EC_width, top_align_y)))
            # insts_specs.append(i3.PlaceRelative("align2", "ec_0:out", (-EC_width, bot_align_y)))
            insts_specs.append(i3.PlaceRelative("align1", 'ec_0:out', (0, top_align_y)))
            insts_specs.append(i3.PlaceRelative("align2", "ec_0:out", (0, bot_align_y)))

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            # ports = {}
            # ports += i3.expose_ports(self.instances, {'sbend_lu:in': 'in1',})
            for row in range(self.n_rows):
                # ports["ec_{}:out".format(row)] = 'fib_{}'.format(row + 1)
                ports += i3.expose_ports(self.instances, {"wg_{}:out".format(row): 'wg_{}'.format(row + 1)})
                # ports["wg_{}:out".format(row)] = 'wg_{}'.format(row + 1)
            return ports


if __name__ == '__main__':
    # WBG1 = custom_amwbg(apodization=30, wbg_length=100, period=0.3, grating_width=0.16)
    #
    # lo = lo
    lo = ECrow()
    # lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('ECrow.gds')
