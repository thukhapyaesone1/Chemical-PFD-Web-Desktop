import { useEffect, useRef } from "react";
import { Image as KonvaImage, Transformer, Circle, Group } from "react-konva";
import useImage from "use-image";
import Konva from "konva";
import { CanvasItemImageProps } from "./types";

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
  const [image] = useImage(item.svg || item.icon);
  const groupRef = useRef<Konva.Group>(null);
  const trRef = useRef<Konva.Transformer>(null);

  useEffect(() => {
    if (isSelected && trRef.current && groupRef.current) {
      trRef.current.nodes([groupRef.current]);
      trRef.current.getLayer()?.batchDraw();
    }
  }, [isSelected]);

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

    // Reset scale to 1 and change width/height instead
    node.scaleX(1);
    node.scaleY(1);

    const updatedItem = {
      ...item,
      x: node.x(),
      y: node.y(),
      width: Math.max(5, item.width * scaleX),
      height: Math.max(5, item.height * scaleY),
      rotation: node.rotation(),
    };

    onChange(updatedItem);
    onTransformEnd?.(updatedItem);
  };

  return (
    <>
      <Group
        ref={groupRef}
        x={item.x}
        y={item.y}
        width={item.width}
        height={item.height}
        rotation={item.rotation}
        draggable
        onDragEnd={handleDragEnd}
        onTransformEnd={handleTransformEnd}
      >
        <KonvaImage
          onClick={onSelect}
          onTap={onSelect}
          image={image}
          x={0}
          y={0}
          width={item.width}
          height={item.height}
        />
      </Group>

      {/* Render Transformer */}
      {isSelected && (
        <Transformer
          ref={trRef}
          boundBoxFunc={(oldBox, newBox) => {
            // limit resize
            if (newBox.width < 5 || newBox.height < 5) {
              return oldBox;
            }
            return newBox;
          }}
        />
      )}

      {/* Render grips AFTER transformer so they appear on top */}
      {/* Show grips when: component is selected OR when drawing a connection */}
      {(isSelected || isDrawingConnection) && item.grips && item.grips.map((grip, index) => {
        // Calculate grip position based on percentage coordinates
        // NOTE: grips.json uses bottom-left origin (Y=0 at bottom, Y=100 at top)
        // Canvas uses top-left origin (Y=0 at top, Y=100 at bottom)
        // So we need to invert the Y coordinate: canvasY = 100 - gripsJsonY
        const gripX = item.x + (grip.x / 100) * item.width;
        const gripY = item.y + ((100 - grip.y) / 100) * item.height;

        const isHovered = hoveredGrip?.itemId === item.id && hoveredGrip?.gripIndex === index;

        return (
          <Circle
            key={index}
            x={gripX}
            y={gripY}
            radius={isDrawingConnection ? 6 : 5}
            fill={isHovered ? "#22c55e" : "#3b82f6"}
            stroke="#ffffff"
            strokeWidth={isHovered ? 3 : 2}
            opacity={isDrawingConnection && !isSelected ? 0.7 : 1}
            listening={true}
            onMouseDown={(e) => {
              e.cancelBubble = true;
              onGripMouseDown?.(item.id, index, gripX, gripY);
            }}
            onMouseEnter={(e) => {
              onGripMouseEnter?.(item.id, index);
              // Change cursor to pointer
              const stage = e.target.getStage();
              if (stage) {
                stage.container().style.cursor = 'pointer';
              }
            }}
            onMouseLeave={(e) => {
              onGripMouseLeave?.();
              // Reset cursor
              const stage = e.target.getStage();
              if (stage) {
                stage.container().style.cursor = 'default';
              }
            }}
          />
        );
      })}
    </>
  );
};