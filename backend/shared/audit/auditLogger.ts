export class AuditLogger {
  static log(event: string, payload: any) {
    console.log(`[AUDIT] ${event}`, {
      timestamp: new Date().toISOString(),
      payload,
    });
  }
}
