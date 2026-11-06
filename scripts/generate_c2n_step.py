# Generate C2N_Edge_Connector.step as a valid B-Rep solid STEP file
def generate_step_box(filename, name, xmin, xmax, ymin, ymax, zmin, zmax):
    content = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('KiCad 9.0 Solid Model'), '2;1');
FILE_NAME('{name}.step', '2026-11-05T10:00:00', ('Alessio Iodice'), ('MuDIsTInf'), 'Open CASCADE STEP processor 7.7', 'KiCad 9.0', 'Unknown');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));
ENDSEC;
DATA;
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard', 'automotive_design', 2000, #2);
#2 = APPLICATION_CONTEXT('core data for automotive mechanical design processes');
#3 = SHAPE_DEFINITION_REPRESENTATION(#4, #10);
#4 = PRODUCT_DEFINITION_SHAPE('', '', #5);
#5 = PRODUCT_DEFINITION('design', '', #6, #9);
#6 = PRODUCT_DEFINITION_FORMATION('', '', #7);
#7 = PRODUCT('{name}', '{name}', '', (#8));
#8 = PRODUCT_CONTEXT('', #2, 'mechanical');
#9 = PRODUCT_DEFINITION_CONTEXT('part definition', #2, 'design');
#10 = ADVANCED_BREP_SHAPE_REPRESENTATION('', (#11, #15), #190);
#11 = AXIS2_PLACEMENT_3D('', #12, #13, #14);
#12 = CARTESIAN_POINT('', (0.0, 0.0, 0.0));
#13 = DIRECTION('', (0.0, 0.0, 1.0));
#14 = DIRECTION('', (1.0, 0.0, 0.0));
#15 = MANIFOLD_SOLID_BREP('', #16);
#16 = CLOSED_SHELL('', (#101, #102, #103, #104, #105, #106));

#20 = CARTESIAN_POINT('', ({xmin:.4f}, {ymin:.4f}, {zmin:.4f}));
#21 = CARTESIAN_POINT('', ({xmax:.4f}, {ymin:.4f}, {zmin:.4f}));
#22 = CARTESIAN_POINT('', ({xmax:.4f}, {ymax:.4f}, {zmin:.4f}));
#23 = CARTESIAN_POINT('', ({xmin:.4f}, {ymax:.4f}, {zmin:.4f}));
#24 = CARTESIAN_POINT('', ({xmin:.4f}, {ymin:.4f}, {zmax:.4f}));
#25 = CARTESIAN_POINT('', ({xmax:.4f}, {ymin:.4f}, {zmax:.4f}));
#26 = CARTESIAN_POINT('', ({xmax:.4f}, {ymax:.4f}, {zmax:.4f}));
#27 = CARTESIAN_POINT('', ({xmin:.4f}, {ymax:.4f}, {zmax:.4f}));

#30 = VERTEX_POINT('', #20);
#31 = VERTEX_POINT('', #21);
#32 = VERTEX_POINT('', #22);
#33 = VERTEX_POINT('', #23);
#34 = VERTEX_POINT('', #24);
#35 = VERTEX_POINT('', #25);
#36 = VERTEX_POINT('', #26);
#37 = VERTEX_POINT('', #27);

#40 = DIRECTION('', (1.0, 0.0, 0.0));
#41 = DIRECTION('', (0.0, 1.0, 0.0));
#42 = DIRECTION('', (-1.0, 0.0, 0.0));
#43 = DIRECTION('', (0.0, -1.0, 0.0));
#44 = DIRECTION('', (0.0, 0.0, 1.0));
#45 = DIRECTION('', (0.0, 0.0, -1.0));

#46 = VECTOR('', #40, 1.0);
#47 = VECTOR('', #41, 1.0);
#48 = VECTOR('', #42, 1.0);
#49 = VECTOR('', #43, 1.0);
#50 = VECTOR('', #44, 1.0);

#51 = LINE('', #20, #46);
#52 = LINE('', #21, #47);
#53 = LINE('', #22, #48);
#54 = LINE('', #23, #49);
#55 = LINE('', #24, #46);
#56 = LINE('', #25, #47);
#57 = LINE('', #26, #48);
#58 = LINE('', #27, #49);
#59 = LINE('', #20, #50);
#60 = LINE('', #21, #50);
#61 = LINE('', #22, #50);
#62 = LINE('', #23, #50);

#71 = EDGE_CURVE('', #30, #31, #51, .T.);
#72 = EDGE_CURVE('', #31, #32, #52, .T.);
#73 = EDGE_CURVE('', #32, #33, #53, .T.);
#74 = EDGE_CURVE('', #33, #30, #54, .T.);
#75 = EDGE_CURVE('', #34, #35, #55, .T.);
#76 = EDGE_CURVE('', #35, #36, #56, .T.);
#77 = EDGE_CURVE('', #36, #37, #57, .T.);
#78 = EDGE_CURVE('', #37, #34, #58, .T.);
#79 = EDGE_CURVE('', #30, #34, #59, .T.);
#80 = EDGE_CURVE('', #31, #35, #60, .T.);
#81 = EDGE_CURVE('', #32, #36, #61, .T.);
#82 = EDGE_CURVE('', #33, #37, #62, .T.);

#83 = ORIENTED_EDGE('', *, *, #71, .T.);
#84 = ORIENTED_EDGE('', *, *, #72, .T.);
#85 = ORIENTED_EDGE('', *, *, #73, .T.);
#86 = ORIENTED_EDGE('', *, *, #74, .T.);
#87 = ORIENTED_EDGE('', *, *, #75, .T.);
#88 = ORIENTED_EDGE('', *, *, #76, .T.);
#89 = ORIENTED_EDGE('', *, *, #77, .T.);
#90 = ORIENTED_EDGE('', *, *, #78, .T.);
#91 = ORIENTED_EDGE('', *, *, #79, .T.);
#92 = ORIENTED_EDGE('', *, *, #80, .T.);
#93 = ORIENTED_EDGE('', *, *, #81, .T.);
#94 = ORIENTED_EDGE('', *, *, #82, .T.);
#95 = ORIENTED_EDGE('', *, *, #71, .F.);
#96 = ORIENTED_EDGE('', *, *, #72, .F.);
#97 = ORIENTED_EDGE('', *, *, #73, .F.);
#98 = ORIENTED_EDGE('', *, *, #74, .F.);
#99 = ORIENTED_EDGE('', *, *, #75, .F.);
#100 = ORIENTED_EDGE('', *, *, #76, .F.);

#111 = EDGE_LOOP('', (#83, #92, #99, #91));
#112 = EDGE_LOOP('', (#84, #93, #100, #92));
#113 = EDGE_LOOP('', (#85, #94, #90, #93));
#114 = EDGE_LOOP('', (#86, #91, #87, #94));
#115 = EDGE_LOOP('', (#83, #84, #85, #86));
#116 = EDGE_LOOP('', (#87, #88, #89, #90));

#121 = FACE_OUTER_BOUND('', #111, .T.);
#122 = FACE_OUTER_BOUND('', #112, .T.);
#123 = FACE_OUTER_BOUND('', #113, .T.);
#124 = FACE_OUTER_BOUND('', #114, .T.);
#125 = FACE_OUTER_BOUND('', #115, .T.);
#126 = FACE_OUTER_BOUND('', #116, .T.);

#131 = PLANE('', #141);
#132 = PLANE('', #142);
#133 = PLANE('', #143);
#134 = PLANE('', #144);
#135 = PLANE('', #145);
#136 = PLANE('', #146);

#141 = AXIS2_PLACEMENT_3D('', #20, #43, #40);
#142 = AXIS2_PLACEMENT_3D('', #21, #40, #41);
#143 = AXIS2_PLACEMENT_3D('', #22, #41, #42);
#144 = AXIS2_PLACEMENT_3D('', #23, #42, #43);
#145 = AXIS2_PLACEMENT_3D('', #20, #45, #41);
#146 = AXIS2_PLACEMENT_3D('', #24, #44, #40);

#101 = ADVANCED_FACE('', (#121), #131, .T.);
#102 = ADVANCED_FACE('', (#122), #132, .T.);
#103 = ADVANCED_FACE('', (#123), #133, .T.);
#104 = ADVANCED_FACE('', (#124), #134, .T.);
#105 = ADVANCED_FACE('', (#125), #135, .T.);
#106 = ADVANCED_FACE('', (#126), #136, .T.);

#190 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#191)) 
GLOBAL_UNIT_ASSIGNED_CONTEXT((#192, #193, #194)) 
REPRESENTATION_CONTEXT('Context #1', '3D Context with UNIT and UNCERTAINTY') );
#191 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07), #192, 'distance_accuracy_value', 'confusion accuracy');
#192 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI., .METRE.) );
#193 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($, .RADIAN.) );
#194 = ( NAMED_UNIT(*) SI_UNIT($, .STERADIAN.) SOLID_ANGLE_UNIT() );

ENDSEC;
END-ISO-10303-21;
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

generate_step_box(
    r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\3dmodels\C2N_Edge_Connector.step",
    "C2N_Edge_Connector",
    -2.5, 22.3, -4.5, 4.5, 0.0, 11.5
)
print("Generated C2N_Edge_Connector.step")
