import { Suspense, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, RoundedBox } from '@react-three/drei'
import { colorDe } from '../colors'

// Caja 3D que gira sola y muestra el nombre del producto
function Caja3D({ producto }) {
  const ref = useRef()
  useFrame((_, delta) => {
    ref.current.rotation.y += delta * 0.6
  })
  const nombre = producto ? producto.name : 'Tu producto'
  const precio = producto ? `Bs ${Number(producto.price).toFixed(2)}` : ''
  return (
    <group ref={ref}>
      <RoundedBox args={[2.2, 2.2, 2.2]} radius={0.15} smoothness={4}>
        <meshStandardMaterial color={colorDe(producto)} metalness={0.25} roughness={0.35} />
      </RoundedBox>
      <Suspense fallback={null}>
        {[0, Math.PI / 2, Math.PI, -Math.PI / 2].map((rot, i) => (
          <group key={i} rotation={[0, rot, 0]}>
            <Text position={[0, 0.2, 1.12]} fontSize={0.26} maxWidth={1.9} textAlign="center" color="white" anchorX="center" anchorY="middle">
              {nombre}
            </Text>
            <Text position={[0, -0.45, 1.12]} fontSize={0.22} color="#fde68a" anchorX="center" anchorY="middle">
              {precio}
            </Text>
          </group>
        ))}
      </Suspense>
    </group>
  )
}

export function Product3DViewer({ product }) {
  return (
    <div className="relative h-80 w-full rounded-2xl overflow-hidden bg-gradient-to-b from-slate-800 to-slate-950 ring-1 ring-white/10">
      <Canvas camera={{ position: [3, 2, 4.2] }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[3, 5, 3]} intensity={1.4} />
        <pointLight position={[-4, -2, -3]} intensity={0.6} />
        <Caja3D producto={product} />
        <OrbitControls enableZoom={false} />
      </Canvas>
      <span className="absolute bottom-3 left-1/2 -translate-x-1/2 text-xs text-slate-300 bg-black/40 px-3 py-1 rounded-full">
        🖱️ Arrastra para girar el modelo 3D
      </span>
    </div>
  )
}
