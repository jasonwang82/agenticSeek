export default function LoginPage() {
	return (
		<div className="container py-8">
			<h1 className="mb-6 text-xl font-semibold">登录 / 注册</h1>
			<div className="grid gap-6 md:grid-cols-2">
				<form className="space-y-4">
					<div>
						<label className="block text-sm text-neutral-600">邮箱</label>
						<input className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
					</div>
					<div>
						<label className="block text-sm text-neutral-600">密码</label>
						<input type="password" className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
					</div>
					<button className="rounded bg-neutral-900 px-4 py-2 text-sm text-white">邮箱登录（敬请期待）</button>
				</form>
				<div>
					<p className="mb-3 text-sm text-neutral-600">第三方登录（占位）</p>
					<div className="flex gap-3">
						<button className="rounded border border-neutral-300 px-4 py-2 text-sm">微信</button>
						<button className="rounded border border-neutral-300 px-4 py-2 text-sm">支付宝</button>
					</div>
				</div>
			</div>
		</div>
	);
}