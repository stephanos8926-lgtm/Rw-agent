register_tool("hello_from_lua", "Say hello to someone from Lua", '{"type": "object", "properties": {"name": {"type": "string", "description": "The name to say hello to"}}, "required": ["name"]}', function(args)
    return "Hello, " .. args.name .. ", from Lua Plugin!"
end)
