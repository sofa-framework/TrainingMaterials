def createScene(rootNode):

	rootNode.name = "RootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("FreeMotionAnimationLoop", name="animation_loop") # 1. Required for Lagrangian constraints
	rootNode.addObject("BlockGaussSeidelConstraintSolver", name="constraint_solver", maxIterations=1000, tolerance=0.001) # 2. Solver that will compute the Lagrangian multiplier value

	
	rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
												     "Sofa.Component.LinearSolver.Iterative","Sofa.Component.ODESolver.Backward",
													 "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
													 "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
													 "Sofa.Component.Visual","Sofa.Component.Mapping.Linear","Sofa.GL.Component.Rendering3D",
													 "Sofa.Component.Constraint.Projective","Sofa.Component.Engine.Select","Sofa.Component.Collision.Geometry",
													 "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Detection.Algorithm",
													 "Sofa.Component.Collision.Response.Contact", "Sofa.GUI.Component","Sofa.Component.AnimationLoop",
													 "Sofa.Component.Constraint.Lagrangian.Correction","Sofa.Component.Constraint.Lagrangian.Correction",
													 "Sofa.Component.Constraint.Lagrangian.Solver","Sofa.Component.LinearSolver.Direct",
													 "Sofa.Component.Constraint.Lagrangian.Model"])

	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")
	rootNode.addObject("ConstraintAttachButtonSetting", name="mouse_config")
	
	rootNode.addObject("VisualStyle", name="visual_options", displayFlags="showForceFields showCollisionModels showBehaviorModels showDetectionOutputs")

	rootNode.addObject("CollisionPipeline", name="collision_pipeline")
	rootNode.addObject("BruteForceBroadPhase", name="broad_phase")
	rootNode.addObject("BVHNarrowPhase", name="narrow_phase")
	rootNode.addObject("MinProximityIntersection", name="narrow_phase_intersection", alarmDistance="10", contactDistance="1")
	rootNode.addObject("CollisionResponse", name="collision_response", response="FrictionContactConstraint",responseParams="mu=0.5") # 3. Formulate contacts as Lagrangian constraints, specifying response="LagrangianContactConstraint"

	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("SparseLDLSolver", name="direct_linear_solver", template="CompressedRowSparseMatrixd") # Linear solver used to inverse A (LDL factorization)
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", totalMass=0.5)
	
	mechanicalModel.addObject("BoxROI", name="box_ROI", box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.state_container.position.linkpath,
							  tetrahedra=mechanicalModel.topology_container.tetrahedra.linkpath)
	mechanicalModel.addObject("FixedLagrangianConstraint", name="fixed_boundary_lagrangian", indices=mechanicalModel.box_ROI.indices.linkpath) # For better convergence, use fixed constraint expressed as Lagrangian constraint
	mechanicalModel.addObject("LinearSolverConstraintCorrection", name="apply_corrective_motion")  # 4. Define the way the Schur complement is computed

	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject("MeshSTLLoader", name="mesh_loader_surface", filename="../PneuNets_remeshed.stl")
	visualModel.addObject("OglModel", name="visual_model", src=visualModel.mesh_loader_surface.linkpath, color=[0.7, 0.7, 0.7, 1])
	visualModel.addObject("BarycentricMapping", name="visual_mapping", input="@../state_container", output="@visual_model")
	

	collisionlModel = mechanicalModel.addChild("Collision")
	collisionlModel.addObject("MeshTopology", name="topology_container", src=visualModel.mesh_loader_surface.linkpath) 
	collisionlModel.addObject("MechanicalObject", name="storing_forces")
	collisionlModel.addObject("TriangleCollisionModel", name="triangle_collision_model") # Remove the contactStiffness which becomes meaningless
	collisionlModel.addObject("BarycentricMapping", name="collision_mapping", input="@../state_container", output="@storing_forces")
	
    
	fallingParticle = rootNode.addChild("ParticleToCollideWith")
	fallingParticle.addObject("EulerImplicitSolver", name="integration_scheme")
	fallingParticle.addObject("CGLinearSolver", name="iterative_linear_solver", iterations=200, tolerance=1e-09, threshold=1e-09)
	fallingParticle.addObject("MechanicalObject", template="Vec3", name="particle_DOF", position=[-170, 80, 0], showObject=True)
	fallingParticle.addObject("UniformMass", name="nodal_mass", totalMass=0.1)
	fallingParticle.addObject("ConstantForceField", name="nodal_force", totalForce=[0,-50,0], indices=0)
	fallingParticle.addObject("SphereCollisionModel", name="sphere_collision_model", radius=10) # Remove the contactStiffness which becomes meaningless
	fallingParticle.addObject("UncoupledConstraintCorrection", name="apply_corrective_motion", defaultCompliance=10) # 4. Define the way the Schur complement is computed
    
    
