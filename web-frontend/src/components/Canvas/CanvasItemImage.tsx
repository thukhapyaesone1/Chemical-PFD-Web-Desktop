import { useEffect, useRef } from "react";
import {
  Image as KonvaImage,
  Transformer,
  Circle,
  Group,
  Text,
} from "react-konva";
import useImage from "use-image";
import Konva from "konva";

import { CanvasItemImageProps } from "./types";

const LABEL_OFFSET = 4;

export const CanvasItemImage = ({
  item,
  isSelected,
  onSelect,
  onChange,
  onDragEnd,
  onTransformEnd,
  onGripMouseDown,
  onGripMouseEnter,
  onGripMouseLeave,
  isDrawingConnection = false,
  hoveredGrip = null,
}: CanvasItemImageProps) => {
  const [image] = useImage(item.svg || item.icon, "anonymous");

  const groupRef = useRef<Konva.Group>(null);
  const trRef = useRef<Konva.Transformer>(null);

  useEffect(() => {
    if (isSelected && trRef.current && groupRef.current) {
      trRef.current.nodes([groupRef.current]);
      trRef.current.getLayer()?.batchDraw();
    }
  }, [isSelected, item.width, item.height, item.x, item.y, item.rotation]);

  const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
    const updatedItem = {
      ...item,
      x: e.target.x(),
      y: e.target.y(),
    };

    onChange(updatedItem);
    onDragEnd?.(updatedItem);
  };

  const handleTransformEnd = () => {
    const node = groupRef.current;

    if (!node) return;

    const scaleX = node.scaleX();
    const scaleY = node.scaleY();

    node.scaleX(1);
    node.scaleY(1);

    const updatedItem = {
      ...item,
      x: node.x(),
      y: node.y(),
      width: Math.max(5, item.width * Math.abs(scaleX)),
      height: Math.max(5, item.height * Math.abs(scaleY)),
      rotation: node.rotation(),
    };

    onChange(updatedItem);
    onTransformEnd?.(updatedItem);
  };

  const labelText = item.label || item.name;

  const labelX = item.x;
  const labelY = item.y + item.height + LABEL_OFFSET;

  return (
    <>
      {/* ================= IMAGE (Selectable / Transformable) ================= */}
      <Group
        ref={groupRef}
        draggable
        height={item.height}
        rotation={item.rotation}
        width={item.width}
        x={item.x}
        y={item.y}
        scaleX={1}
        scaleY={1}
        onDragEnd={handleDragEnd}
        onTransformEnd={handleTransformEnd}
      >
        {(() => {
          // Calculate aspect-fit dimensions
          if (!image) {
            // Fallback if image not loaded yet
            return <KonvaImage image={undefined} width={item.width} height={item.height} />;
          }

          const imgWidth = image.naturalWidth || item.width;
          const imgHeight = image.naturalHeight || item.height;

          if (imgWidth === 0 || imgHeight === 0) return null;

          const aspectRatio = imgWidth / imgHeight;
          const containerRatio = item.width / item.height;

          let renderWidth = item.width;
          let renderHeight = item.height;
          let renderX = 0;
          let renderY = 0;

          if (containerRatio > aspectRatio) {
            // Container is wider than image -> fit height
            renderHeight = item.height;
            renderWidth = renderHeight * aspectRatio;
            renderX = (item.width - renderWidth) / 2;
          } else {
            // Container is taller/narrower -> fit width
            renderWidth = item.width;
            renderHeight = renderWidth / aspectRatio;
            renderY = (item.height - renderHeight) / 2;
          }

          return (
            <KonvaImage
              height={renderHeight}
              image={image}
              width={renderWidth}
              x={renderX}
              y={renderY}
              onClick={(e) => onSelect(e as any)}
              onTap={(e) => onSelect(e as any)}
            />
          );
        })()}

      </Group>

      {/* ================= LABEL (Visual Only, Behind Everything) ================= */}

      <Text
        align="center"
        fill="#374151"
        fontFamily="Arial, sans-serif"
        fontSize={12}
        listening={false}
        text={labelText}
        width={item.width + 100} // Increase width to prevent wrapping
        x={labelX + item.width / 2}
        y={labelY + 2}
        offsetX={(item.width + 100) / 2} // Center align
      />

      {/* ================= TRANSFORMER ================= */}
      {isSelected && (
        <Transformer
          ref={trRef}
          rotateEnabled={false} // Disable rotation
          keepRatio={true} // Enforce aspect ratio scaling
          flipEnabled={false} // Disable flipping to prevent negative scale issues
          enabledAnchors={[
            'top-left',
            'top-right',
            'bottom-left',
            'bottom-right',
          ]}
          boundBoxFunc={(oldBox, newBox) => {
            // Prevent shrinking too small
            if (newBox.width < 10 || newBox.height < 10) {
              return oldBox;
            }
            return newBox;
          }}
        />
      )}

      {/* ================= GRIPS (Always On Top) ================= */}
      {(isSelected || isDrawingConnection) &&
        item.grips?.map((grip, index) => {
          const gripX = item.x + (grip.x / 100) * item.width;
          const gripY = item.y + ((100 - grip.y) / 100) * item.height;

          const isHovered =
            hoveredGrip?.itemId === item.id && hoveredGrip?.gripIndex === index;

          return (
            <Circle
              key={index}
              listening
              fill={isHovered ? "#22c55e" : "#3b82f6"}
              opacity={isDrawingConnection && !isSelected ? 0.7 : 1}
              radius={isDrawingConnection ? 6 : 5}
              stroke="#ffffff"
              strokeWidth={isHovered ? 3 : 2}
              x={gripX}
              y={gripY}
              onMouseDown={(e) => {
                e.cancelBubble = true;
                onGripMouseDown?.(item.id, index, gripX, gripY);
              }}
              onMouseEnter={(e) => {
                onGripMouseEnter?.(item.id, index);
                e.target
                  .getStage()
                  ?.container()
                  .style.setProperty("cursor", "pointer");
              }}
              onMouseLeave={(e) => {
                onGripMouseLeave?.();
                e.target
                  .getStage()
                  ?.container()
                  .style.setProperty("cursor", "default");
              }}
            />
          );
        })}
    </>
  );
};
