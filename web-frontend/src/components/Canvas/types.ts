// Reusable types for canvas and components
export interface ComponentItem {
  name: string;
  icon: string;
  svg: string;
  class: string;
  object: string;
  args: any[];
}

export interface CanvasItem extends ComponentItem {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
}

export interface StagePosition {
  x: number;
  y: number;
}

export interface CanvasDimensions {
  width: number;
  height: number;
}

export interface ComponentLibrarySidebarProps {
  components: Record<string, Record<string, ComponentItem>>;
  onDragStart: (e: React.DragEvent, item: ComponentItem) => void;
  onSearch?: (query: string) => void;
  onCategoryChange?: (category: string) => void;
  initialSearchQuery?: string;
  selectedCategory?: string;
  className?: string;
}

export interface CanvasItemImageProps {
  item: CanvasItem;
  isSelected: boolean;
  onSelect: () => void;
  onChange: (newAttrs: CanvasItem) => void;
  onDragEnd?: (item: CanvasItem) => void;
  onTransformEnd?: (item: CanvasItem) => void;
}

export interface CanvasPropertiesSidebarProps {
  items: CanvasItem[];
  selectedItemId: number | null;
  onSelectItem: (itemId: number) => void;
  onDeleteItem: (itemId: number) => void;
  onUpdateItem?: (itemId: number, updates: Partial<CanvasItem>) => void;
  className?: string;
  showAllItemsByDefault?: boolean;
}
