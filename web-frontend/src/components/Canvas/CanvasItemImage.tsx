import { useEffect, useRef } from "react";
import { Image as KonvaImage, Transformer } from "react-konva";
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
}: CanvasItemImageProps) => {
  const [image] = useImage(item.svg || item.icon);
  const shapeRef = useRef<Konva.Image>(null);
  const trRef = useRef<Konva.Transformer>(null);

  useEffect(() => {
    if (isSelected && trRef.current && shapeRef.current) {
      trRef.current.nodes([shapeRef.current]);
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
    const node = shapeRef.current;
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
      width: Math.max(5, node.width() * scaleX),
      height: Math.max(5, node.height() * scaleY),
      rotation: node.rotation(),
    };

    onChange(updatedItem);
    onTransformEnd?.(updatedItem);
  };

  return (
    <>
      <KonvaImage
        onClick={onSelect}
        onTap={onSelect}
        ref={shapeRef}
        image={image}
        x={item.x}
        y={item.y}
        width={item.width}
        height={item.height}
        rotation={item.rotation}
        draggable
        onDragEnd={handleDragEnd}
        onTransformEnd={handleTransformEnd}
      />
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
    </>
  );
};