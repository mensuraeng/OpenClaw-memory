import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { randomUUID } from 'crypto';

const DATA_PATH = path.join(process.cwd(), 'data', 'notifications.json');

export interface Notification {
  id: string;
  timestamp: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  link?: string;
  metadata?: Record<string, unknown>;
}

interface NotificationsResponse {
  notifications: Notification[];
  unreadCount: number;
}

async function loadNotifications(): Promise<Notification[]> {
  try {
    const data = await fs.readFile(DATA_PATH, 'utf-8');
    return JSON.parse(data);
  } catch {
    return [];
  }
}

async function saveNotifications(notifications: Notification[]): Promise<void> {
  const dir = path.dirname(DATA_PATH);
  try { await fs.access(dir); } catch { await fs.mkdir(dir, { recursive: true }); }
  await fs.writeFile(DATA_PATH, JSON.stringify(notifications, null, 2));
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const onlyUnread = searchParams.get('unread') === 'true';
    const limit = parseInt(searchParams.get('limit') || '50');

    let notifications = await loadNotifications();
    if (onlyUnread) notifications = notifications.filter((n) => !n.read);
    notifications.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    notifications = notifications.slice(0, limit);
    const unreadCount = (await loadNotifications()).filter((n) => !n.read).length;

    return NextResponse.json<NotificationsResponse>({ notifications, unreadCount });
  } catch (error) {
    console.error('Failed to get notifications:', error);
    return NextResponse.json({ error: 'Failed to get notifications' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    if (!body.title || !body.message) {
      return NextResponse.json({ error: 'Missing required fields: title, message' }, { status: 400 });
    }
    const validTypes = ['info', 'success', 'warning', 'error'];
    const type = body.type || 'info';
    if (!validTypes.includes(type)) {
      return NextResponse.json({ error: `Invalid type. Must be one of: ${validTypes.join(', ')}` }, { status: 400 });
    }
    const notifications = await loadNotifications();
    const newNotification: Notification = {
      id: randomUUID(),
      timestamp: new Date().toISOString(),
      title: body.title,
      message: body.message,
      type,
      read: false,
      link: body.link,
      metadata: body.metadata,
    };
    notifications.unshift(newNotification);
    await saveNotifications(notifications);
    return NextResponse.json(newNotification, { status: 201 });
  } catch (error) {
    console.error('Failed to create notification:', error);
    return NextResponse.json({ error: 'Failed to create notification' }, { status: 500 });
  }
}

// PATCH: mark notification as read (lightweight, acceptable in v1)
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, readAll } = body;
    const notifications = await loadNotifications();
    if (readAll) {
      notifications.forEach((n) => { n.read = true; });
    } else if (id) {
      const n = notifications.find((n) => n.id === id);
      if (!n) return NextResponse.json({ error: 'Notification not found' }, { status: 404 });
      n.read = true;
    } else {
      return NextResponse.json({ error: 'Missing id or readAll' }, { status: 400 });
    }
    await saveNotifications(notifications);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update notification:', error);
    return NextResponse.json({ error: 'Failed to update notification' }, { status: 500 });
  }
}

// DELETE disabled in v1 — reduces auditability
export async function DELETE() {
  return NextResponse.json(
    { error: 'notification deletion disabled in mission control v1', code: 'DISABLED_IN_V1' },
    { status: 403 }
  );
}
