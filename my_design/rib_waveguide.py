from si_fab import all as pdk
from ipkiss3 import all as i3


ribWg = pdk.SiRibWaveguideTemplate()
ribWg.Layout(core_width=0.85,
             cladding_width=0.85 + 7+7)


class customTaper(i3.PCell):
    _name_prefix = "customTaper"
    taperW1 = i3.PositiveNumberProperty(default=0.45, doc="taperW1.")
    taperW2 = i3.PositiveNumberProperty(default=0.45, doc="taperW2.")
    taperW3 = i3.PositiveNumberProperty(default=1, doc="taperW3.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    rib_trace_template = i3.TraceTemplateProperty(
        default=pdk.SiRibWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            taperW1 = self.taperW1
            taperW2 = self.taperW2
            taperW3 = self.taperW3
            taperLength = self.taperLength
            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer
            cladding1 = self.rib_trace_template.cladding_layer

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
                end_width=taperW3 + 7,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)

            elems_to_merge_cladding1 = [i3.Wedge(
                layer=cladding,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1,
                end_width=taperW3,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding1, cladding1)

            return elems

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0, trace_template=ribWg)
            return ports

class customTaper_rib(i3.PCell):
    _name_prefix = "customTaper"
    taperW1 = i3.PositiveNumberProperty(default=0.45, doc="taperW1.")
    taperW2 = i3.PositiveNumberProperty(default=1, doc="taperW2.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")

    rib_trace_template = i3.TraceTemplateProperty(
        default=pdk.SiRibWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            taperW1 = self.taperW1
            taperW2 = self.taperW2
            taperLength = self.taperLength
            core = self.rib_trace_template.core_layer
            cladding = self.rib_trace_template.cladding_layer
            cladding1=self.trace_template.cladding_layer
            elems_to_merge_core = [i3.Wedge(
                layer=core,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=0.45,
                end_width=taperW1,
            )]
            elems += i3.merge_elements(elems_to_merge_core, core)

            elems_to_merge_cladding = [i3.Wedge(
                layer=cladding,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=0.45 ,
                end_width=taperW2 ,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)

            elems_to_merge_cladding1 = [i3.Wedge(
                layer=cladding1,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=0.45+7,
                end_width=taperW2+7,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding1, cladding1)
            return elems

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0, trace_template=ribWg)
            return ports
class customribWavegudie(i3.PCell):
    _name_prefix = "customribWavegudie"
    n_o_waveguide = i3.IntProperty(default=4, doc="number of waveguide")
    Width3 = i3.PositiveNumberProperty(default=1, doc="rib Width.")
    Length = i3.PositiveNumberProperty(default=200, doc="waveguide length.")
    Width1 = i3.PositiveNumberProperty(default=0.45, doc="narrow width.")
    Width2 = i3.PositiveNumberProperty(default=0.45, doc="rib core width.")
    taperLength = i3.PositiveNumberProperty(default=50., doc="taperLength.")
    bendRadius = i3.PositiveNumberProperty(default=20., doc="bendRadius.")
    gapBetweenWg = i3.PositiveNumberProperty(default=42., doc="gapBetweenWg.")
    # rounding_algorithm = i3.DefinitionProperty(default=None, doc="rounding_algorithm.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    rib_trace_template = i3.TraceTemplateProperty(
        default=pdk.SiRibWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    # gap = i3.PositiveNumberProperty(default=10., doc="gap between GC output and the input port of devices.")
    # taperW2 = i3.PositiveNumberProperty(default=3., doc="taperW2.")
    # taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            n_o_waveguide = self.n_o_waveguide
            Length = self.Length
            Width1 = self.Width1
            Width2 = self.Width2
            Width3 = self.Width3
            taperLength = self.taperLength
            bendRadius = self.bendRadius
            gapBetweenWg = self.gapBetweenWg
            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer
            ribCladding = self.rib_trace_template.cladding_layer

            elems_to_merge_core = []
            elems_to_merge_cladding = []
            # WgBend90
            for i in range(int(n_o_waveguide)):
                elems_to_merge_core.append(
                    i3.Rectangle(layer=core,
                                 center=(taperLength + Length / 2, gapBetweenWg * i),
                                 # box_size=(Width2, Length))
                                 box_size=(Length, Width2))
                )
                elems_to_merge_cladding.append(
                    i3.Rectangle(layer=cladding,
                                 center=(taperLength + Length / 2, gapBetweenWg * i),
                                 box_size=(Length, Width3+ 7))
                )
                #2/0
                elems_to_merge_ribCladding = [
                    i3.Rectangle(
                        layer=ribCladding,
                        center=(taperLength + Length / 2, gapBetweenWg * i),
                        box_size=(Length, Width3),
                    )
                ]
                elems += i3.merge_elements(elems_to_merge_ribCladding, ribCladding)
            elems += i3.merge_elements(elems_to_merge_core, core)
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)
            return elems

        def _generate_instances(self, insts):
            # gap = self.gap
            # gcc32 = pdk.GCrow()
            n_o_waveguide = self.n_o_waveguide
            bendRadius = self.bendRadius
            Length = self.Length
            taperLength = self.taperLength
            gapBetweenWg = self.gapBetweenWg
            trace_template = self.trace_template
            # rounding_algorithm = self.rounding_algorithm
            # taper = customTaper(
            #     taperW1=self.Width1,
            #     taperW2=self.Width2,
            #     taperLength=self.taperLength,
            # )
            taper = customTaper_rib(
                taperW1=self.Width2,
                taperW2=self.Width3,
                taperLength=self.taperLength,
            )

            insts_insts = dict()
            insts_specs = list()
            for i in range(int(n_o_waveguide)):
                insts_insts[f'taper{i}_L'] = taper
                insts_specs.append(
                    i3.Place(f'taper{i}_L:in', (0.0, gapBetweenWg * i))
                )

                insts_insts[f'taper{i}_R'] = taper
                insts_specs.append(
                    i3.Place(f'taper{i}_R:out', (taperLength + Length, gapBetweenWg * i), angle=180.)
                )

            if int(n_o_waveguide) != 1:
                for i in range(int(n_o_waveguide)):
                    if i >= int(n_o_waveguide)-1:
                        break
                    else:
                        if i % 2 == 0:
                            insts_specs.append(
                                i3.ConnectManhattan(f'taper{i}_R:in', f'taper{i+1}_R:in',
                                                    bend_radius=bendRadius,

                                                    )
                            )
                        else:
                            insts_specs.append(
                                i3.ConnectManhattan(f'taper{i}_L:in', f'taper{i + 1}_L:in',
                                                    bend_radius=bendRadius,

                                                    )
                            )

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            n_o_waveguide = self.n_o_waveguide
            gapBetweenWg = self.gapBetweenWg
            Length = self.Length
            bendRadius = self.bendRadius
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            if int(n_o_waveguide)%2 == 0:
                ports += i3.OpticalPort(name='out', position=(0., gapBetweenWg*(int(n_o_waveguide)-1)), angle=180.0)
            else:
                ports += i3.OpticalPort(name='out', position=(taperLength*2 + Length, gapBetweenWg*(int(n_o_waveguide)-1)), angle=0.0)

            return ports
class ribWireTaper(i3.PCell):
    _name_prefix = "ribWireTaper"
    # wireCoreWidth = i3.PositiveNumberProperty(default=0.45, doc="wireCoreWidth.")
    ribwidth=i3.PositiveNumberProperty(default=1, doc="ribCoreWidth.")
    ribCoreWidth = i3.PositiveNumberProperty(default=0.45, doc="ribCoreWidth.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")
    preTaperLength = i3.PositiveNumberProperty(default=50., doc="preTaperLength.")
    minWidth = i3.PositiveNumberProperty(default=0.1, doc="minWidth.")
    wire_trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )
    rib_trace_template = i3.TraceTemplateProperty(
        default=pdk.SiRibWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            # wireCoreWidth = self.wireCoreWidth
            wireCoreWidth = self.wire_trace_template.core_width
            wireCladdingWidth = self.wire_trace_template.cladding_width
            ribCoreWidth = self.ribCoreWidth
            # ribCoreWidth = self.rib_trace_template.core_width
            taperLength = self.taperLength
            preTaperLength = self.preTaperLength
            minWidth = self.minWidth
            core = self.wire_trace_template.core_layer
            cladding = self.wire_trace_template.cladding_layer
            ribwidth=self.ribwidth
            ribCladding = self.rib_trace_template.cladding_layer
            ribExpend = (self.rib_trace_template.cladding_width - ribCoreWidth) / 2
            #1/0
            elems_to_merge_core = [i3.Wedge(
                layer=core,
                begin_coord=(-preTaperLength, 0),
                end_coord=(0, 0.),
                begin_width=wireCoreWidth,
                end_width=ribCoreWidth,
            ),
                i3.Wedge(
                    layer=core,
                    begin_coord=(0, 0),
                    end_coord=(taperLength, 0.),
                    begin_width=ribCoreWidth,
                    end_width=ribCoreWidth,
                )
            ]
            elems += i3.merge_elements(elems_to_merge_core, core)
            #50/0包层
            elems += i3.Rectangle(
                layer=cladding,
                center=((-preTaperLength+taperLength)/2,0),
                box_size=(preTaperLength+taperLength,wireCoreWidth + 7),
            )
            #脊波导
            elems_to_merge_ribCladding = [
                i3.Rectangle(
                    layer=ribCladding,
                    center=(taperLength / 2, 0),
                    box_size=(taperLength, ribwidth),
                )
            ]
            elems += i3.merge_elements(elems_to_merge_ribCladding, ribCladding)
            return elems

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            preTaperLength = self.preTaperLength
            ribWg = self.rib_trace_template
            ports += i3.OpticalPort(name='in', position=(-preTaperLength, 0.), angle=180.0)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0, trace_template=ribWg)
            return ports

if __name__ == '__main__':
    testtaper = customribWavegudie()
    testtaper.Layout().visualize()
    testtaper.Layout().write_gdsii('TESTrib.gds')