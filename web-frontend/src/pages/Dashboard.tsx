import { Button, Card, CardHeader, CardBody, CardFooter, Divider, Chip, Input, Dropdown, DropdownTrigger, DropdownMenu, DropdownItem } from "@heroui/react";
import { useNavigate } from "react-router-dom";
import { useState, useMemo } from "react";
import { CiFilter } from "react-icons/ci";

// Mock Data
const projects = [
  { id: 101, title: "Distillation Unit A", updated: "2 hrs ago", status: "Draft" },
  { id: 102, title: "Reactor Process Flow", updated: "1 day ago", status: "Review" },
  { id: 103, title: "Heat Exchanger Loop", updated: "5 days ago", status: "Final" },
];

export default function Dashboard() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("recent");
  const [sizeFilter, setSizeFilter] = useState("all");

  const createNewProject = () => {
    const newId = Date.now();
    navigate(`/editor/${newId}`);
  };

  const filteredProjects = useMemo(() => {
    let list = [...projects];

    if (search.trim() !== "") {
      list = list.filter((p) => p.title.toLowerCase().includes(search.toLowerCase()));
    }

    if (sortBy === "alpha") {
      list.sort((a, b) => a.title.localeCompare(b.title));
    }

    // Optional: mock size filter (small/medium/large projects)
    if (sizeFilter !== "all") {
      list = list.filter((p) => {
        if (sizeFilter === "small") return p.id < 102;
        if (sizeFilter === "medium") return p.id >= 102 && p.id < 103;
        if (sizeFilter === "large") return p.id >= 103;
        return true;
      });
    }

    return list;
  }, [search, sortBy, sizeFilter]);

  return (
    <div className="flex flex-col gap-6">
      {/* Header Section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">My Projects</h1>
          <p className="text-gray-500">Manage your PFD diagrams</p>
        </div>
        <Button color="primary" onPress={createNewProject}>
          + New Diagram
        </Button>
      </div>

      {/* Search + Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <Input
          isClearable
          radius="lg"
          placeholder="Search projects..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* Combined Filter Dropdown */}
        <Dropdown>
          <DropdownTrigger>
            <Button
                isIconOnly
                variant="light"
                className="text-foreground hover:text-primary"
            >
                <CiFilter size={22} />
            </Button>
          </DropdownTrigger>
          <DropdownMenu aria-label="Filter and sort options">
            {/* Sort Section */}
            <DropdownItem key="sort-header" isReadOnly className="text-xs font-semibold opacity-70">
              Sort By
            </DropdownItem>
            <DropdownItem 
              key="recent" 
              onPress={() => setSortBy("recent")}
              className={sortBy === "recent" ? "bg-primary/10" : ""}
            >
              Most Recent
            </DropdownItem>
            <DropdownItem 
              key="alpha" 
              onPress={() => setSortBy("alpha")}
              className={sortBy === "alpha" ? "bg-primary/10" : ""}
            >
              Alphabetical
            </DropdownItem>
            
            <DropdownItem key="divider" isReadOnly className="opacity-0" />
            
            {/* Size Filter Section */}
            <DropdownItem key="size-header" isReadOnly className="text-xs font-semibold opacity-70">
              Size Filter
            </DropdownItem>
            <DropdownItem 
              key="all" 
              onPress={() => setSizeFilter("all")}
              className={sizeFilter === "all" ? "bg-primary/10" : ""}
            >
              All Projects
            </DropdownItem>
            <DropdownItem 
              key="small" 
              onPress={() => setSizeFilter("small")}
              className={sizeFilter === "small" ? "bg-primary/10" : ""}
            >
              Small
            </DropdownItem>
            <DropdownItem 
              key="medium" 
              onPress={() => setSizeFilter("medium")}
              className={sizeFilter === "medium" ? "bg-primary/10" : ""}
            >
              Medium
            </DropdownItem>
            <DropdownItem 
              key="large" 
              onPress={() => setSizeFilter("large")}
              className={sizeFilter === "large" ? "bg-primary/10" : ""}
            >
              Large
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>

      <Divider />

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((proj) => (
          <Card
            key={proj.id}
            className="p-2 hover:scale-[1.01] transition-transform cursor-pointer"
            isPressable
            onPress={() => navigate(`/editor/${proj.id}`)}
          >
            <CardHeader className="flex gap-3">
              <div className="bg-primary/10 p-2 rounded-lg text-2xl">📄</div>
              <div className="flex flex-col">
                <p className="text-md font-bold">{proj.title}</p>
                <p className="text-small text-default-500">Edited {proj.updated}</p>
              </div>
            </CardHeader>
            <Divider />
            <CardBody>
              <p className="text-gray-500 text-sm">
                Chemical process flow diagram for standard industrial unit...
              </p>
            </CardBody>
            <CardFooter className="flex justify-between">
              <Chip size="sm" color={proj.status === "Final" ? "success" : "warning"} variant="flat">
                {proj.status}
              </Chip>
              <Button size="sm" variant="light" color="primary">
                Open Editor
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}