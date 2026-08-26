export class LatestRequest {
    private generation = 0;

    begin(): number {
        return ++this.generation;
    }

    cancel(): void {
        ++this.generation;
    }

    isCurrent(token: number): boolean {
        return token === this.generation;
    }
}

export class RetryablePromiseCache<TKey, TValue> {
    private readonly entries = new Map<TKey, Promise<TValue>>();
    private readonly loader: (key: TKey) => PromiseLike<TValue>;

    constructor(loader: (key: TKey) => PromiseLike<TValue>) {
        this.loader = loader;
    }

    get(key: TKey): Promise<TValue> {
        let promise = this.entries.get(key);
        if (promise)
            return promise;

        promise = Promise.resolve(this.loader(key));
        this.entries.set(key, promise);
        promise.catch(() => {
            if (this.entries.get(key) === promise)
                this.entries.delete(key);
        });
        return promise;
    }

    clear(): void {
        this.entries.clear();
    }
}
