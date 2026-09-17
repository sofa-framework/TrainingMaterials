def createScene(rootNode):

	from Sofa.Units.Definitions import s, m, mm, N, kg, kPa  
	from Sofa.Units.UnitSystem import MechanicalUnitSystem

	scene_unit = MechanicalUnitSystem(s, mm, kg)

	rootNode.name = "RootNode"
	rootNode.dt = scene_unit(0.01, s)
	rootNode.gravity = [0, scene_unit(-9.81, N/kg), 0]

	rootNode.addObject("DefaultAnimationLoop", name="animation_loop", computeBoundingBox=False)
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Direct','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D'])
	
	rootNode.addObject("VisualStyle", name="visual_options",  displayFlags="showForceFields showWireframe")

	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("SparseLDLSolver", name="linear_solver", template="CompressedRowSparseMatrixMat3x3d")
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=scene_unit(800, kPa))
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", massDensity=scene_unit(1e3, kg/m**3))
		
    # Adding a rendering model using the same mesh as for the mechanics
    # in a dedicated node connected to the mechanical model using a Mapping
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject('OglModel', name="visual_model", topology="@../topology_container", color="1 0.8 0.2 0.5") # Orange color with transparency
	visualModel.addObject('IdentityMapping', name="visual_mapping", input="@../state_container", output="@visual_model") # Identity mapping connecting the identic topology
