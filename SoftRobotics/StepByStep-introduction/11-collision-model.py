def createScene(rootNode):

	rootNode.name = "RootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("DefaultAnimationLoop", name="animation_loop", computeBoundingBox=False)
	
	rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
												     "Sofa.Component.LinearSolver.Iterative","Sofa.Component.ODESolver.Backward",
													 "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
													 "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
													 "Sofa.Component.Visual","Sofa.Component.Mapping.Linear","Sofa.GL.Component.Rendering3D",
													 "Sofa.Component.Constraint.Projective","Sofa.Component.Engine.Select","Sofa.Component.Collision.Geometry",
													 "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Detection.Algorithm",
													 "Sofa.Component.Collision.Response.Contact", "Sofa.GUI.Component"])

	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")
	rootNode.addObject("AttachBodyButtonSetting", name="mouse_config", stiffness=1)
	
	rootNode.addObject("VisualStyle", name="visual_options", displayFlags="showForceFields showCollisionModels showBehaviorModels showDetectionOutputs")

    ##########################################
    # Collision pipeline definition : broad phase / narrow phase / response
	rootNode.addObject("CollisionPipeline", name="collision_pipeline")
	rootNode.addObject("BruteForceBroadPhase", name="broad_phase") # Broad phase
	rootNode.addObject("BVHNarrowPhase", name="narrow_phase") # Narrow phase
	rootNode.addObject("MinProximityIntersection", name="narrow_phase_intersection", alarmDistance="0.5", contactDistance="0.25") #Intersection method used for the narrow phase
	rootNode.addObject("CollisionResponse", name="collision_response", response="PenalityContactForceField") # Reponse method when a contact is detected in the narrow phase
	##########################################
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("CGLinearSolver", name="iterative_linear_solver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", totalMass=0.5)
	
	mechanicalModel.addObject("BoxROI", name="box_ROI", box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.state_container.position.linkpath,
							  tetrahedra=mechanicalModel.topology_container.tetrahedra.linkpath)
	mechanicalModel.addObject("FixedProjectiveConstraint", name="fixed_boundary", indices=mechanicalModel.box_ROI.indices.linkpath)

	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject("MeshSTLLoader", name="mesh_loader_surface", filename="../PneuNets_remeshed.stl")
	visualModel.addObject("OglModel", name="visual_model", src=visualModel.mesh_loader_surface.linkpath, color=[0.7, 0.7, 0.7, 1])
	visualModel.addObject("BarycentricMapping", name="visual_mapping", input="@../state_container", output="@visual_model")
	
	##########################################
	# Collision representation of the finger object
	collisionlModel = mechanicalModel.addChild("Collision")
	collisionlModel.addObject("MeshTopology", name="topology_container", src=visualModel.mesh_loader_surface.linkpath) # Use the same mesh topology than the visual model
	collisionlModel.addObject("MechanicalObject", name="storing_forces") # Mechanical object storing the DoFs corresponding to the contact points and associated forces
	collisionlModel.addObject("TriangleCollisionModel", name="triangle_collision_model", contactStiffness=3) # Triangular primitives used at the narrow phase
	collisionlModel.addObject("BarycentricMapping", name="collision_mapping", input="@../state_container", output="@storing_forces") # Barycentric mapping connecting the two representations with different topologies
	
    
    ##########################################
	# Additional object which will collide with the finger
	# fallingParticle = rootNode.addChild("ParticleToCollideWith")
	# fallingParticle.addObject("EulerImplicitSolver", name="integration_scheme")
	# fallingParticle.addObject("CGLinearSolver", name="iterative_linear_solver", iterations=200, tolerance=1e-09, threshold=1e-09)
	# fallingParticle.addObject("MechanicalObject", template="Rigid3", name="particle_DOF", position=[-170, 80, 0,  0,0,0,1], showObject=True)
	# fallingParticle.addObject("UniformMass", name="nodal_mass", totalMass=0.1)
	# fallingParticle.addObject("ConstantForceField", name="nodal_force", totalForce=[0,-50,0,0,0,0], indices=0)
	# fallingParticle.addObject("SphereCollisionModel", name="sphere_collision_model", radius=10, contactStiffness=100)
	##########################################
    
    
