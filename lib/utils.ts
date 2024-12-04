import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import {sha256} from "viem";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
export const generateSampleHash = (message: string): `0x${string}` => {
  return sha256(new TextEncoder().encode(message));
};
