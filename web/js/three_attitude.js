const container3D = document.getElementById('three-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, container3D.clientWidth / container3D.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container3D.clientWidth, container3D.clientHeight);
container3D.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0xffffff, 1);
pointLight.position.set(10, 20, 10);
scene.add(pointLight);

const rocketGroup = new THREE.Group();
const bodyMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.3 });
const noseMat = new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.2 });
const bodyGeo = new THREE.CylinderGeometry(0.4, 0.4, 3, 16);
const bodyMesh = new THREE.Mesh(bodyGeo, bodyMat);
rocketGroup.add(bodyMesh);

const noseGeo = new THREE.ConeGeometry(0.4, 1.2, 16);
const noseMesh = new THREE.Mesh(noseGeo, noseMat);
noseMesh.position.y = 2.1;
rocketGroup.add(noseMesh);

scene.add(rocketGroup);
camera.position.set(0, 0, 7);

function updateRocketAttitude(pitch, yaw, roll) {
    rocketGroup.rotation.x = THREE.MathUtils.degToRad(roll || 0);
    rocketGroup.rotation.y = THREE.MathUtils.degToRad(yaw || 0);
    rocketGroup.rotation.z = THREE.MathUtils.degToRad(-(pitch || 0) + 90);
}

function animate3D() {
    requestAnimationFrame(animate3D);
    renderer.render(scene, camera);
}
animate3D();
