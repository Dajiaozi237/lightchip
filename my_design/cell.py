from si_fab import all as pdk
from ipkiss3 import all as i3
from ipkiss.process.layer_map import GenericGdsiiPPLayerInputMap
from si_fab.technology import TECH
# si_fab\technology
import os


# TECH = pdk.TECH


class GC1550(i3.GDSCell):
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    def _default_filename(self):
        file_path = os.path.dirname(__file__) + '/../pcell/GC620_2.GDS'
        # return 'GC620_2.gds' # path to the gdsii file that contains the cell to be imported
        return file_path  # path to the gdsii file that contains the cell to be imported

    def _default_cell_name(self):
        return 'GC_620'  # name of the cell to be imported inside the gdsii file.

    class Layout(i3.GDSCell.Layout):
        # print(os.path)
        def _default_layer_map(self):
            # core = self.trace_template.default.Layout.view.core_layer
            core = self.trace_template.core_layer
            # cladding = self.trace_template.default.Layout.view.cladding_layer
            cladding = self.trace_template.cladding_layer
            layermap = GenericGdsiiPPLayerInputMap(
                ignore_undefined_mappings=True,
                pplayer_map={
                    # only define a mapping for the Core layer.
                    # the cladding layer will be ignored, because ignore_undefined_mappings is set to True

                    (core.process, core.purpose): (1, 0),
                    # (TECH.PPLAYER.SI.process, TECH.PPLAYER.SI.purpose): (1, 0),
                    (TECH.PPLAYER.SHALLOW.process, TECH.PPLAYER.SHALLOW.purpose): (2, 0),
                    (cladding.process, cladding.purpose): (50, 2),
                    # (TECH.PPLAYER.NONE.process, TECH.PPLAYER.NONE.purpose): (50, 2),
                })
            return layermap

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name='GCIO', position=(0.0, 0.0),
                                    angle=180.0)  # We have to manually set the ports as this info is not in the gdsii file yet
            ports += i3.VerticalOpticalPort(name="vertical_in",
                                            position=(105.0, 0.0),
                                            inclination=90.0,
                                            angle=0.0)  # For the fiber a vertical port is used.

            return ports


class TextGC(i3.PCell):
    # _name_prefix = "TextGC"

    class Layout(i3.LayoutView):
        n_rows = i3.IntProperty(doc="Number of GC rows", default=0)

        def _generate_elements(self, elems):
            labelText = f'GC:{self.n_rows + 1}'
            elems = i3.PolygonText(
                layer=TECH.PPLAYER.DOC,
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


class GCrow(i3.Circuit):
    _name_prefix = "GRATING_COUPLER_MATRIX"
    n_rows = i3.IntProperty(doc="Number of GC rows", default=32)
    gc = i3.ChildCellProperty(doc="Grating coupler cell (only for 1D gratings)", default=GC1550())
    gc_sep_y = i3.PositiveNumberProperty(doc="Vertical separation between the grating couplers", default=127.0)
    wg_str_len = i3.NonNegativeNumberProperty(doc="Length straight wavelength at the GC port", default=10.0)
    wg_type = i3.StringProperty(default="wide", doc="type of waveguide: wide or narrow")
    bd_radius = i3.NonNegativeNumberProperty(default=10, doc="bd_radius")
    textMarker = i3.BoolProperty(default=0, doc="show textMarker")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    FA_marker_sep = i3.NonNegativeNumberProperty(default=5000., doc="separation of 2 alignment markers")
    FA_top_thick = i3.NonNegativeNumberProperty(default=1000., doc="FA_top_thick")
    # FA_marker_width = i3.NonNegativeNumberProperty(default=50., doc="shape of FA_marker")
    # FA_marker_length = i3.NonNegativeNumberProperty(default=300., doc="shape of FA_marker")

    def _default_insts(self):
        insts = {}
        wg_len = self.wg_str_len
        textMarker = self.textMarker
        # core = self.trace_template.core_layer
        # cladding = self.trace_template.cladding_layer
        for row in range(self.n_rows):
            wg =pdk.SiWireWaveguideTemplate()
            wg.Layout(core_width=0.45)
            wg.Layout(cladding_width=0.45 + 7)
            conn_wg = i3.RoundedWaveguide(trace_template=wg)
            conn_wg.Layout(
                shape=[
                    (0.0, 0.0),
                    (-wg_len, 0.0),
                ],
            )
            insts["gc_{}".format(row)] = self.gc
            insts["wg_{}".format(row)] = conn_wg
            if textMarker == 1:
                insts["text_{}".format(row)] = TextGC().Layout(n_rows=row)
        # insts["align"] = i3.ShapeCross(thickness=30.)
        cross = i3.LayoutCell(name="align").Layout(
            elements=[
                # i3.Cross(layer=TECH.PPLAYER.SI, thickness=10., box_size=150),
                i3.Cross(layer=TECH.PPLAYER.NONE, thickness=10., box_size=150),
                # i3.Cross(layer=TECH.PPLAYER.SI, thickness=30.),
            ]
        )
        insts["align1"] = cross
        insts["align2"] = cross
        return insts

    def _default_specs(self):
        specs = []
        tt2 = SiWireWaveguideTemplate()
        # tt2.Layout(core_width=3.0, cladding_width=3.0 + 7)
        tt2.Layout(core_width=1.2, cladding_width=1.2 + 7)
        wg_type = self.wg_type
        bd_radius = self.bd_radius
        textMarker = self.textMarker
        for row in range(self.n_rows):
            y_loc = row * self.gc_sep_y
            # angle = 180.0 - self.gc.get_default_view(i3.LayoutView).ports['opt1'].angle
            angle = 0.0
            specs.append(i3.Place("gc_{}:GCIO".format(row), (0, y_loc), angle))
            specs.append(i3.Place("wg_{}:in".format(row), (0, y_loc), 180.0))
            if textMarker == 1:
                specs.append(i3.PlaceRelative("text_{}:LOC".format(row), "gc_{}:GCIO".format(row), (-50-70, -25)))
                # insts["text_{}".format(row)] = TextGC().Layout(n_rows=row)
        n_rows = self.n_rows
        gc_sep_y = self.gc_sep_y
        control_points = [
            (0.0, -200.0),
            (-250, gc_sep_y * (n_rows - 3)),
            (0, gc_sep_y * (n_rows - 1) + 200)]

        if wg_type == 'narrow':
            temp = i3.ConnectManhattan('wg_0:out', 'wg_{}:out'.format(n_rows - 1),
                                       bend_radius=bd_radius,
                                       control_points=control_points,
                                       )
        else:
            temp = i3.ConnectManhattanTapered('wg_0:out', 'wg_{}:out'.format(n_rows - 1),
                                              bend_radius=bd_radius,
                                              control_points=control_points,
                                              straight_trace_template=tt2,
                                              taper_length=150.,
                                              # taper_length=100.,
                                              min_straight_section_length=100.,
                                              )
        # lo = temp.get_default_view(i3.LayoutView)
        # a = lo.trace_length()
        # print(a)
        specs.append(temp)

        # lo = self.gc.size_info()
        # GC_width = lo.width
        GC_width = 130.
        y_loc = (self.n_rows - 1) * self.gc_sep_y
        # print(y_loc)
        top_align_y = (self.FA_marker_sep - y_loc) / 2 + y_loc
        bot_align_y = 0 - (self.FA_marker_sep - y_loc) / 2
        specs.append(i3.PlaceRelative("align1", 'wg_0:out', (-GC_width+25 + self.FA_top_thick, top_align_y)))
        specs.append(i3.PlaceRelative("align2", "wg_0:out", (-GC_width+25 + self.FA_top_thick, bot_align_y)))
        return specs

    def _default_exposed_ports(self):
        ports = {}
        for row in range(self.n_rows):
            ports["gc_{}:GCIO".format(row)] = 'fib_{}'.format(row + 1)
            ports["wg_{}:out".format(row)] = 'wg_{}'.format(row + 1)
            # ports += i3.expose_ports(self.instances,
            #                          {"gc_{}:GCIO".format(row): 'fib_{}'.format(row + 1)})
            # ports += i3.expose_ports(self.instances,
            #                          {"wg_{}:out".format(row): 'wg_{}'.format(row + 1)})
        return ports