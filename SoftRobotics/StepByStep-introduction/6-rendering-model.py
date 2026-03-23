def createScene(rootNode):

	rootNode.name = "RootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("DefaultAnimationLoop", name="animation_loop", computeBoundingBox=False)
	
	rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
												     "Sofa.Component.LinearSolver.Iterative","Sofa.Component.ODESolver.Backward",
													 "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
													 "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
													 "Sofa.Component.Visual","Sofa.GL.Component.Rendering3D"])
	rootNode.addObject("VisualStyle", name="visual_options", displayFlags="showForceFields")
	
	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("CGLinearSolver", name="iterative_linear_solver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", totalMass=0.5)
	
    # Adding a rendering model using the same mesh as for the mechanics
	mechanicalModel.addObject("OglModel", name="visual_model", topology="@topology_container") # Connect with the object topology (could be connected to the mesh loader too)
