import { Button } from "@heroui/button";
import { Link } from "@heroui/link";
import { Navbar, NavbarBrand, NavbarContent, NavbarItem } from "@heroui/navbar";
import {
  Popover,
  PopoverTrigger,
  Avatar,
  PopoverContent,
  User,
  Divider,
} from "@heroui/react";
import { useLocation, useNavigate } from "react-router-dom";

import { ThemeSwitch } from "./theme-switch";
export const CNavbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const username = localStorage.getItem("username") || "Guest";

  return (
    <>
      <Navbar isBordered maxWidth="xl">
        <NavbarBrand
          className="cursor-pointer"
          onClick={() => navigate("/dashboard")}
        >
          <p className="font-bold text-inherit text-xl">🧪 ChemPFD</p>
        </NavbarBrand>

        <NavbarContent className="hidden sm:flex gap-4" justify="center">
          <NavbarItem isActive={location.pathname === "/dashboard"}>
            <Link color="foreground" href="/dashboard">
              Dashboard
            </Link>
          </NavbarItem>
          <NavbarItem isActive={location.pathname === "/components"}>
            <Link color="foreground" href="/components">
              Components DB
            </Link>
          </NavbarItem>
          {/* <NavbarItem isActive={location.pathname === "/reports"}> */}
          {/* <Link color="foreground" href="/reports">Reports</Link> */}
          {/* </NavbarItem>  */}
        </NavbarContent>

        <NavbarContent justify="end">
          <NavbarItem>
            <ThemeSwitch />
          </NavbarItem>
          <NavbarItem>
            {/* Profile Popover */}
            <Popover placement="bottom-end" showArrow={true}>
              <PopoverTrigger>
                <Avatar
                  isBordered
                  as="button"
                  className="transition-transform"
                  color="primary"
                  name={username[0]?.toUpperCase() || "U"}
                  size="sm"
                  src=""
                />
              </PopoverTrigger>
              <PopoverContent className="p-1 w-60">
                <div className="px-1 py-2 w-full">
                  <User
                    avatarProps={{
                      src: "",
                      name: username[0]?.toUpperCase() || "U"
                    }}
                    classNames={{
                      base: "gap-8",
                      name: "text-default-800",
                      description: "text-default-500",
                    }}
                    description=""
                    name={username}
                  />
                </div>
                <Divider />
                <div className="flex flex-col gap-1 p-1">
                  <Button className="justify-start" size="sm" variant="light">
                    My Settings
                  </Button>
                  <Button className="justify-start" size="sm" variant="light">
                    Help & Feedback
                  </Button>
                  <Divider className="my-1" />
                  <Button
                    className="justify-start"
                    color="danger"
                    size="sm"
                    variant="flat"
                    onPress={() => navigate("/login")}
                  >
                    Log Out
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
          </NavbarItem>
        </NavbarContent>
      </Navbar>
    </>
  );
};
