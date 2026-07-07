import api from "./api";

export type CurrentUserProfile = {
  id: number;
  name: string;
  email: string;
  roles: string[];
};

const PROFILE_STORAGE_KEY = "erp_current_user";

export function saveCurrentUserProfile(profile: CurrentUserProfile): void {
  const serialized = JSON.stringify(profile);

  localStorage.setItem(PROFILE_STORAGE_KEY, serialized);
  sessionStorage.setItem(PROFILE_STORAGE_KEY, serialized);
}

export function getStoredProfile(): CurrentUserProfile | null {
  const raw = localStorage.getItem(PROFILE_STORAGE_KEY) || sessionStorage.getItem(PROFILE_STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as CurrentUserProfile;

    if (!Array.isArray(parsed.roles)) {
      return { ...parsed, roles: [] };
    }

    return parsed;
  } catch {
    return null;
  }
}

export function clearStoredProfile(): void {
  localStorage.removeItem(PROFILE_STORAGE_KEY);
  sessionStorage.removeItem(PROFILE_STORAGE_KEY);
}

export function hasAnyRole(userRoles: string[] | undefined, acceptedRoles: string[]): boolean {
  if (!userRoles || userRoles.length === 0) {
    return false;
  }

  return acceptedRoles.some((role) => userRoles.includes(role));
}

export async function refreshCurrentUserProfile(): Promise<CurrentUserProfile> {
  const response = await api.get("/me");
  const data = response.data as CurrentUserProfile;

  const normalized: CurrentUserProfile = {
    id: data.id,
    name: data.name,
    email: data.email,
    roles: Array.isArray(data.roles) ? data.roles : [],
  };

  saveCurrentUserProfile(normalized);
  return normalized;
}
