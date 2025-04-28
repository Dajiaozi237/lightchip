from si_fab import all as pdk
from ipkiss3 import all as i3
from ECrow_Pcell import ECrow

tt2 = pdk.SiWireWaveguideTemplate()
tt2.Layout(core_width=0.41)


class customTaper2(i3.PCell):
    _name_prefix = "customTaper"
    taperW1 = i3.PositiveNumberProperty(default=0.45, doc="taperW1.")
    taperW2 = i3.PositiveNumberProperty(default=3, doc="taperW2.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            taperW1 = self.taperW1
            taperW2 = self.taperW2
            taperLength = self.taperLength
            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer

            elems_to_merge_core = [i3.Wedge(
                layer=core,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1,
                end_width=taperW2,
            )]
            elems += i3.merge_elements(elems_to_merge_core, core)

            elems_to_merge_cladding = [i3.Wedge(
                layer=cladding,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1 + 7,
                end_width=taperW2 + 7,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)
            return elems

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0, trace_template=tt2)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0)
            return ports

class customPBS(i3.PCell):
    _name_prefix = "customPBS"
    Width1 = i3.PositiveNumberProperty(default=0.41, doc="waveguide1 width and waveguide3 width.")
    Width2 = i3.PositiveNumberProperty(default=1.08, doc="waveguide2 width.")
    Width3 = i3.PositiveNumberProperty(default=0.45, doc="waveguide2 width")
    gap_wg = i3.PositiveNumberProperty(default=0.3, doc="gap between waveguide")
    Length1 = i3.PositiveNumberProperty(default=8.5, doc="first coupling length")
    Length2 = i3.FloatProperty(default=0.2, doc="second coupling length")
    Length3 = i3.PositiveNumberProperty(default=9.2, doc="third coupling length")
    rec_length = i3.PositiveNumberProperty(default=10, doc="rectangle length")
    taper_Length = i3.PositiveNumberProperty(default=20, doc="taper length")

    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            Width1 = self.Width1
            Width2 = self.Width2
            gap_wg = self.gap_wg
            Length1 = self.Length1
            Length2 = self.Length2
            Length3 = self.Length3
            rec_length = self.rec_length
            taper_Length = self.taper_Length

            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer

            elems_to_merge_core = [
                i3.Rectangle(layer=core,
                             center=(taper_Length + rec_length / 2, 0),
                             box_size=(rec_length, Width1)),
                i3.Rectangle(layer=core,
                             center=(taper_Length + rec_length + Length1 / 2, 0),
                             box_size=(Length1, Width1)),
                i3.Rectangle(layer=core,
                             center=(taper_Length + rec_length + (Length1 - Length2 + Length3) / 2, -Width1 / 2 - gap_wg - Width2 / 2),
                             box_size=(Length1 - Length2 + Length3, Width2)),
                i3.Rectangle(layer=core,
                             center=(taper_Length + rec_length + Length1 - Length2 + Length3 / 2, -Width1 - gap_wg * 2 - Width2),
                             box_size=(Length3, Width1)),
                i3.Rectangle(layer=core,
                             center=(taper_Length + rec_length + Length1 - Length2 + Length3 + rec_length / 2, -Width1 - gap_wg * 2 - Width2),
                             box_size=(rec_length, Width1))
            ]

            elems_to_merge_cladding = [
                i3.Rectangle(layer=cladding,
                             center=(taper_Length + (rec_length * 2 + Length1 - Length2 + Length3) / 2, -gap_wg - (Width1 + Width2)/2),
                             box_size=(rec_length * 2 + Length1 - Length2 + Length3, Width1 * 2 + gap_wg *2 + Width2 + 7)),
            ]

            elems += i3.merge_elements(elems_to_merge_core, core)
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)

            return elems

        def _generate_instances(self, insts):
            Width1 = self.Width1
            Width2 = self.Width2
            Width3 = self.Width3
            Length1 = self.Length1
            Length2 = self.Length2
            Length3 = self.Length3
            rec_length = self.rec_length
            taper_Length = self.taper_Length
            gap_wg = self.gap_wg

            taper1 = customTaper2(
                taperW1=self.Width3,
                taperW2=self.Width1,
                taperLength=self.taper_Length,
            )
            taper2 = customTaper2(
                taperW1=self.Width1,
                taperW2=self.Width3,
                taperLength=self.taper_Length,
            )

            insts_insts = {
                'taper1': taper1,
                'taper2': taper2,
            }

            insts_specs = [
                i3.Place('taper1:in', (0, 0)),
                i3.Place('taper2:in', (taper_Length + rec_length * 2 + Length1 - Length2 + Length3, -Width1 - gap_wg * 2 - Width2)),
            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            Width1 = self.Width1
            Width2 = self.Width2
            Width3 = self.Width3
            Length1 = self.Length1
            Length2 = self.Length2
            Length3 = self.Length3
            rec_length = self.rec_length
            taper_Length = self.taper_Length
            gap_wg = self.gap_wg

            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            ports += i3.OpticalPort(name='out1',
                                    position=(taper_Length + rec_length + Length1, 0),
                                    angle=0, trace_template=tt2)
            ports += i3.OpticalPort(name='out2',
                                    position=(
                                    taper_Length * 2 + rec_length * 2 + Length1 - Length2 + Length3, -Width1 - gap_wg * 2 - Width2),
                                    angle=0,)

            return ports


class PBS_col1(i3.PCell):
    _name_prefix = "PBS_col1"
    gap = i3.PositiveNumberProperty(default=10., doc="gap between GC output and the input port of devices.")

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap

            PBS1 = customPBS(
                Length1=8.5
            )
            PBS2 = customPBS(
                Length1=9.5
            )
            PBS3 = customPBS(
                Length1=10.5
            )
            PBS4 = customPBS(
                Length1=7.5
            )
            PBS5 = customPBS(
                Length1=6.5
            )
            PBS6 = customPBS(
                Length2=-1
            )
            PBS7 = customPBS(
                Length2=0
            )
            PBS8 = customPBS(
                Length2=1
            )
            PBS9 = customPBS(
                Length3=10.2
            )

            taper = customTaper2(
                taperW1=0.41,
                taperW2=0.45,
                taperLength=20,
            )

            insts_insts = {
                'PBS1': PBS1,
                'PBS2': PBS2,
                'PBS3': PBS3,
                'PBS4': PBS4,
                'PBS5': PBS5,
                'PBS6': PBS6,
                'PBS7': PBS7,
                'PBS8': PBS8,
                'PBS9': PBS9,
                'ECrow1': ECrow(n_rows=32, ec_sep_y=127, FA_marker_sep=5000),
            }
            for i in range(1, 10):
                insts_insts[f'taper{i}'] = taper

            output_gap = gap

            insts_specs = [
                i3.Place("ECrow1:wg_1", (0, 0)),

                i3.ConnectManhattan('ECrow1:wg_1', 'ECrow1:wg_32', bend_radius=20, control_points=[
                    i3.START + (750, 1270)
                ]),
                i3.ConnectManhattan('ECrow1:wg_31', 'ECrow1:wg_30', control_points=[
                    i3.START + (20, 0)], ),

                i3.PlaceRelative("PBS1:in", "ECrow1:wg_3", (output_gap, 0)),
                i3.ConnectManhattan("PBS1:in", "ECrow1:wg_3"),
                i3.ConnectManhattan("PBS1:out2", "ECrow1:wg_2", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS2:in", "ECrow1:wg_6", (output_gap, 0)),
                i3.ConnectManhattan("PBS2:in", "ECrow1:wg_6"),
                i3.ConnectManhattan("PBS2:out2", "ECrow1:wg_5", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS3:in", "ECrow1:wg_9", (output_gap, 0)),
                i3.ConnectManhattan("PBS3:in", "ECrow1:wg_9"),
                i3.ConnectManhattan("PBS3:out2", "ECrow1:wg_8", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS4:in", "ECrow1:wg_12", (output_gap, 0)),
                i3.ConnectManhattan("PBS4:in", "ECrow1:wg_12"),
                i3.ConnectManhattan("PBS4:out2", "ECrow1:wg_11", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS5:in", "ECrow1:wg_15", (output_gap, 0)),
                i3.ConnectManhattan("PBS5:in", "ECrow1:wg_15"),
                i3.ConnectManhattan("PBS5:out2", "ECrow1:wg_14", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS6:in", "ECrow1:wg_18", (output_gap, 0)),
                i3.ConnectManhattan("PBS6:in", "ECrow1:wg_18"),
                i3.ConnectManhattan("PBS6:out2", "ECrow1:wg_17", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS7:in", "ECrow1:wg_21", (output_gap, 0)),
                i3.ConnectManhattan("PBS7:in", "ECrow1:wg_21"),
                i3.ConnectManhattan("PBS7:out2", "ECrow1:wg_20", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS8:in", "ECrow1:wg_24", (output_gap, 0)),
                i3.ConnectManhattan("PBS8:in", "ECrow1:wg_24"),
                i3.ConnectManhattan("PBS8:out2", "ECrow1:wg_23", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
                i3.PlaceRelative("PBS9:in", "ECrow1:wg_27", (output_gap, 0)),
                i3.ConnectManhattan("PBS9:in", "ECrow1:wg_27"),
                i3.ConnectManhattan("PBS9:out2", "ECrow1:wg_26", bend_radius=20, control_points=[
                    i3.START + (22, -63.45),
                ], ),
            ]

            for i in range(1, 10):
                insts_specs.append(
                    i3.PlaceRelative(f'taper{i}:in', f'PBS{i}:out1', (50, 20))
                )
                insts_specs.append(
                    i3.ConnectBend(f'taper{i}:in', f'PBS{i}:out1', bend_radius=20, trace_template=tt2)
                )
                insts_specs.append(
                    i3.ConnectManhattan(f'ECrow1:wg_{3 * i + 1}', f'taper{i}:out', bend_radius=20
                )
                )
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         "ECrow1:wg_1": 'loc',
                                     })
            return ports


if __name__ == '__main__':
    c2=customPBS(Length1=8.5),
    # c2 = PBS_col1(
    #     gap=20,
    # )
    c2.Layout().write_gdsii('customPBS.gds')
