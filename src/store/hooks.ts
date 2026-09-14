import { useStore, useSelector, useDispatch } from "react-redux";
import type { AppStore, RootState, AppDispatch } from "@/store/store";

// Adds the proper types to the useStore, useSelector, and useDispatch functions
export const useAppStore = useStore.withTypes<AppStore>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();